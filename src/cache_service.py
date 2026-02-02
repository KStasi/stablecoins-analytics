from datetime import datetime
from sqlalchemy import func
from src.database import BridgeTransaction, SlippageCache


def update_slippage_cache(db) -> None:
    """Update slippage cache for all token pairs."""
    pairs = db.query(
        BridgeTransaction.token_in_id, BridgeTransaction.token_out_id
    ).distinct().all()

    for token_in_id, token_out_id in pairs:
        result = db.query(
            func.avg(BridgeTransaction.slippage).label("avg_slippage"),
            func.count(BridgeTransaction.id).label("tx_count"),
        ).filter(
            BridgeTransaction.token_in_id == token_in_id,
            BridgeTransaction.token_out_id == token_out_id,
        ).first()

        cache = db.query(SlippageCache).filter_by(
            token_in_id=token_in_id, token_out_id=token_out_id
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
                last_updated=datetime.utcnow(),
            )
            db.add(cache)

    db.commit()
