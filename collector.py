import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import func
from database import SessionLocal, Token, BridgeTransaction, SlippageCache, init_db

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Start from December 1st, 2024
START_DATE = "2024-12-01"

# Known token symbols by contract address
KNOWN_TOKENS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",  # ETH
    "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": "USDT",  # ARB
    "0xfde4c96c8593536e31f229ea8f37b2ada2699bb2": "USDT",  # BASE
    "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58": "USDT",  # OP
    "0xc2132d05d31c914a87c6611c10748aeb04b58e8f": "USDT",  # POLYGON
    "0x55d398326f99059ff775485246999027b3197955": "USDT",  # BSC
    "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7": "USDT",  # AVAX
    
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",  # ETH
    "0xaf88d065e77c8cc2239327c5edb3a432268e5831": "USDC",  # ARB
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": "USDC",  # BASE
    "0x0b2c639c533813f4aa9d7837caf62653d097ff85": "USDC",  # OP
    "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359": "USDC",  # POLYGON
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": "USDC",  # BSC
    "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e": "USDC",  # AVAX
}

def parse_asset_id(asset_id: str) -> dict:
    """Parse asset ID to extract chain, address, and symbol"""
    # Format: nep141:eth-0xabc...def.omft.near or nep141:eth.omft.near or nep141:hash
    
    if not asset_id:
        return {"chain": None, "address": None, "symbol": None}
    
    # Remove nep141: prefix and .omft.near suffix if present
    cleaned = asset_id.replace("nep141:", "").replace(".omft.near", "")
    
    chain = None
    address = None
    symbol = None
    
    # Try to parse chain-address format
    if "-" in cleaned:
        parts = cleaned.split("-", 1)
        chain = parts[0]
        address = parts[1]
        
        # Try to get symbol from known addresses
        symbol = KNOWN_TOKENS.get(address.lower())
    else:
        # Just chain name or hash
        chain = cleaned if len(cleaned) < 20 else None
        address = cleaned if len(cleaned) >= 20 else None
    
    return {"chain": chain, "address": address, "symbol": symbol}

def get_or_create_token(db, asset_id: str) -> Token:
    """Get existing token or create new one"""
    token = db.query(Token).filter_by(asset_id=asset_id).first()
    
    if not token:
        parsed = parse_asset_id(asset_id)
        token = Token(
            symbol=parsed["symbol"] or "UNKNOWN",
            asset_id=asset_id,
            chain=parsed["chain"],
            address=parsed["address"]
        )
        db.add(token)
        db.flush()  # Get the ID without committing
    
    return token

def fetch_all_transactions(page: int = 1, per_page: int = 100) -> dict:
    """Fetch one page of transactions"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    params = {
        "page": page,
        "perPage": per_page,
        "startTimestamp": START_DATE,
    }
    
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"  API error: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"  Error: {e}")
        return None

def store_transactions(db, transactions: list):
    """Store transactions and tokens in database"""
    stored_count = 0
    
    for tx in transactions:
        try:
            deposit_key = tx.get("depositAddressAndMemo", "")
            if not deposit_key:
                continue
            
            # Check if already exists
            existing = db.query(BridgeTransaction).filter_by(
                deposit_address_and_memo=deposit_key
            ).first()
            
            if existing:
                continue
            
            # Get or create tokens
            origin_asset = tx.get("originAsset", "")
            dest_asset = tx.get("destinationAsset", "")
            
            if not origin_asset or not dest_asset:
                continue
            
            token_in = get_or_create_token(db, origin_asset)
            token_out = get_or_create_token(db, dest_asset)
            
            # Parse amounts
            amount_in = float(tx.get("amountInFormatted", 0))
            amount_out = float(tx.get("amountOutFormatted", 0))
            
            if amount_in > 0:
                slippage = ((amount_in - amount_out) / amount_in) * 100
            else:
                slippage = 0
            
            # Parse timestamp
            created_at = datetime.fromisoformat(
                tx.get("createdAt", "").replace("Z", "+00:00")
            )
            
            # Create transaction record
            bridge_tx = BridgeTransaction(
                token_in_id=token_in.id,
                token_out_id=token_out.id,
                amount_in=amount_in,
                amount_out=amount_out,
                slippage=slippage,
                deposit_address=tx.get("depositAddress", ""),
                deposit_address_and_memo=deposit_key,
                status=tx.get("status", ""),
                intent_hash=tx.get("intentHashes", ""),
                created_at=created_at
            )
            
            db.add(bridge_tx)
            stored_count += 1
            
        except Exception as e:
            print(f"  Error storing transaction: {e}")
            continue
    
    db.commit()
    return stored_count

def update_slippage_cache(db):
    """Update slippage cache for all token pairs"""
    # Get all unique token pairs
    pairs = db.query(
        BridgeTransaction.token_in_id,
        BridgeTransaction.token_out_id
    ).distinct().all()
    
    for token_in_id, token_out_id in pairs:
        result = db.query(
            func.avg(BridgeTransaction.slippage).label('avg_slippage'),
            func.count(BridgeTransaction.id).label('tx_count')
        ).filter(
            BridgeTransaction.token_in_id == token_in_id,
            BridgeTransaction.token_out_id == token_out_id
        ).first()
        
        cache = db.query(SlippageCache).filter_by(
            token_in_id=token_in_id,
            token_out_id=token_out_id
        ).first()
        
        if cache:
            cache.avg_slippage = result.avg_slippage if result.avg_slippage else None
            cache.tx_count = result.tx_count
            cache.last_updated = datetime.utcnow()
        else:
            cache = SlippageCache(
                token_in_id=token_in_id,
                token_out_id=token_out_id,
                avg_slippage=result.avg_slippage if result.avg_slippage else None,
                tx_count=result.tx_count,
                last_updated=datetime.utcnow()
            )
            db.add(cache)
    
    db.commit()

def collect_data(max_pages: int = 10):
    """Main collection function - fetches all transactions from Dec 1st"""
    print(f"[{datetime.now()}] Starting data collection...")
    print(f"Collecting all transactions since Dec 1, 2024")
    init_db()
    db = SessionLocal()
    
    try:
        total_fetched = 0
        total_stored = 0
        page = 1
        
        while page <= max_pages:
            print(f"\nPage {page}/{max_pages}...")
            
            # Fetch transactions
            data = fetch_all_transactions(page=page, per_page=100)
            
            if not data:
                print("  No data returned, stopping")
                break
            
            transactions = data.get("data", [])
            
            if not transactions or len(transactions) == 0:
                print("  No more transactions")
                break
            
            total_fetched += len(transactions)
            print(f"  Fetched {len(transactions)} transactions")
            
            # Store in database
            stored = store_transactions(db, transactions)
            total_stored += stored
            print(f"  Stored {stored} new transactions (total stored: {total_stored})")
            
            page += 1
            
            # Rate limiting
            time.sleep(5.1)
        
        print(f"\n{'='*60}")
        print(f"Total fetched: {total_fetched}")
        print(f"Total stored: {total_stored}")
        
        # Update cache
        print("\nUpdating slippage cache...")
        update_slippage_cache(db)
        
        print(f"[{datetime.now()}] Data collection completed")
        
    except Exception as e:
        print(f"Error during collection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    collect_data(max_pages=100)  # Collect 100 pages
