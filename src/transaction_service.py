from datetime import datetime
from src.database import BridgeTransaction
from src.parser import get_or_create_token
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
)


def calculate_slippage(amount_in: float, amount_out: float) -> float:
    """Calculate slippage percentage."""
    if amount_in > 0:
        return ((amount_in - amount_out) / amount_in) * 100
    return 0


def parse_transaction(tx: dict, db) -> BridgeTransaction | None:
    """Parse a single transaction from API response into a BridgeTransaction."""
    deposit_key = tx.get(FIELD_DEPOSIT_KEY, "")
    if not deposit_key:
        return None

    existing = db.query(BridgeTransaction).filter_by(
        deposit_address_and_memo=deposit_key
    ).first()
    if existing:
        return None

    origin_asset = tx.get(FIELD_ORIGIN_ASSET, "")
    dest_asset = tx.get(FIELD_DEST_ASSET, "")
    if not origin_asset or not dest_asset:
        return None

    token_in = get_or_create_token(db, origin_asset)
    token_out = get_or_create_token(db, dest_asset)

    amount_in = float(tx.get(FIELD_AMOUNT_IN, 0))
    amount_out = float(tx.get(FIELD_AMOUNT_OUT, 0))
    slippage = calculate_slippage(amount_in, amount_out)

    created_at = datetime.fromisoformat(
        tx.get(FIELD_CREATED_AT, "").replace("Z", "+00:00")
    )

    return BridgeTransaction(
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


def store_transactions(db, transactions: list) -> int:
    """Store transactions in database. Returns count of stored transactions."""
    stored_count = 0

    for tx in transactions:
        try:
            bridge_tx = parse_transaction(tx, db)
            if bridge_tx:
                db.add(bridge_tx)
                stored_count += 1
        except Exception as e:
            print(f"  Error storing transaction: {e}")
            continue

    db.commit()
    return stored_count
