from datetime import datetime
from src.database import BridgeTransaction, Token
from src.parser import parse_asset_id
from src.const import (
    FIELD_DEPOSIT_KEY,
    FIELD_ORIGIN_ASSET,
    FIELD_DEST_ASSET,
    FIELD_AMOUNT_IN,
    FIELD_AMOUNT_OUT,
    FIELD_CREATED_AT,
    FIELD_DEPOSIT_ADDRESS,
    FIELD_STATUS,
    FIELD_INTENT_HASHES,
    UNKNOWN_SYMBOL,
)


def get_oldest_transaction_timestamp(db) -> datetime | None:
    """Get the timestamp of the oldest transaction.

    This allows resuming data collection from where we left off
    by using endTimestamp for proper pagination.
    """
    oldest = (
        db.query(BridgeTransaction.created_at)
        .order_by(BridgeTransaction.created_at.asc())
        .first()
    )
    return oldest[0] if oldest else None


def calculate_slippage(amount_in: float, amount_out: float) -> float:
    """Calculate slippage percentage."""
    if amount_in > 0:
        return ((amount_in - amount_out) / amount_in) * 100
    return 0


def _get_existing_deposit_keys(db, deposit_keys: set[str]) -> set[str]:
    """Batch check for existing transactions by deposit keys."""
    if not deposit_keys:
        return set()
    
    existing = db.query(BridgeTransaction.deposit_address_and_memo).filter(
        BridgeTransaction.deposit_address_and_memo.in_(deposit_keys)
    ).all()
    return {row[0] for row in existing}


def _get_or_create_tokens_bulk(db, asset_ids: set[str]) -> dict[str, Token]:
    """Bulk get or create tokens. Returns a dict mapping asset_id to Token."""
    if not asset_ids:
        return {}
    
    # Fetch all existing tokens in one query
    existing_tokens = db.query(Token).filter(Token.asset_id.in_(asset_ids)).all()
    token_cache = {token.asset_id: token for token in existing_tokens}
    
    # Find missing tokens and create them
    missing_asset_ids = asset_ids - set(token_cache.keys())
    if missing_asset_ids:
        new_tokens = []
        for asset_id in missing_asset_ids:
            parsed = parse_asset_id(asset_id)
            token = Token(
                symbol=parsed["symbol"] or UNKNOWN_SYMBOL,
                asset_id=asset_id,
                chain=parsed["chain"],
                address=parsed["address"],
            )
            new_tokens.append(token)
        
        # Bulk insert new tokens
        db.add_all(new_tokens)
        db.flush()  # Get IDs assigned
        
        # Add to cache
        for token in new_tokens:
            token_cache[token.asset_id] = token
    
    return token_cache


def store_transactions(db, transactions: list) -> int:
    """Store transactions in database using bulk operations. Returns count of stored transactions."""
    if not transactions:
        return 0
    
    # Step 1: Extract all deposit keys and filter out empty ones
    tx_with_keys = []
    for tx in transactions:
        deposit_key = tx.get(FIELD_DEPOSIT_KEY, "")
        if deposit_key:
            tx_with_keys.append((tx, deposit_key))
    
    if not tx_with_keys:
        return 0
    
    # Step 2: Batch check for existing transactions (single query)
    all_deposit_keys = {dk for _, dk in tx_with_keys}
    existing_keys = _get_existing_deposit_keys(db, all_deposit_keys)
    
    # Filter out already existing transactions
    new_transactions = [(tx, dk) for tx, dk in tx_with_keys if dk not in existing_keys]
    
    if not new_transactions:
        return 0
    
    # Step 3: Collect all unique asset IDs needed
    asset_ids = set()
    valid_transactions = []
    for tx, deposit_key in new_transactions:
        origin_asset = tx.get(FIELD_ORIGIN_ASSET, "")
        dest_asset = tx.get(FIELD_DEST_ASSET, "")
        if origin_asset and dest_asset:
            asset_ids.add(origin_asset)
            asset_ids.add(dest_asset)
            valid_transactions.append((tx, deposit_key))
    
    if not valid_transactions:
        return 0
    
    # Step 4: Bulk get/create all tokens (single query + bulk insert)
    token_cache = _get_or_create_tokens_bulk(db, asset_ids)
    
    # Step 5: Build all BridgeTransaction objects
    bridge_transactions = []
    for tx, deposit_key in valid_transactions:
        try:
            origin_asset = tx.get(FIELD_ORIGIN_ASSET, "")
            dest_asset = tx.get(FIELD_DEST_ASSET, "")
            
            token_in = token_cache.get(origin_asset)
            token_out = token_cache.get(dest_asset)
            
            if not token_in or not token_out:
                continue
            
            amount_in = float(tx.get(FIELD_AMOUNT_IN, 0))
            amount_out = float(tx.get(FIELD_AMOUNT_OUT, 0))
            slippage = calculate_slippage(amount_in, amount_out)
            
            created_at = datetime.fromisoformat(
                tx.get(FIELD_CREATED_AT, "").replace("Z", "+00:00")
            )
            
            bridge_tx = BridgeTransaction(
                token_in_id=token_in.id,
                token_out_id=token_out.id,
                amount_in=amount_in,
                amount_out=amount_out,
                slippage=slippage,
                deposit_address=tx.get(FIELD_DEPOSIT_ADDRESS, ""),
                deposit_address_and_memo=deposit_key,
                status=tx.get(FIELD_STATUS, ""),
                intent_hash=tx.get(FIELD_INTENT_HASHES, ""),
                created_at=created_at,
            )
            bridge_transactions.append(bridge_tx)
        except Exception as e:
            print(f"  Error parsing transaction: {e}")
            continue
    
    # Step 6: Bulk insert all transactions
    if bridge_transactions:
        db.add_all(bridge_transactions)
        db.commit()
    
    return len(bridge_transactions)
