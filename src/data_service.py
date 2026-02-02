import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from src.database import SessionLocal, Token, BridgeTransaction
from src.const import (
    SAME_CHAIN_SLIPPAGE,
    UNKNOWN_SYMBOL,
    NA_PLACEHOLDER,
)


def calculate_percentile(values: list, percentile) -> float | None:
    """Calculate percentile or average from list of values."""
    if not values:
        return None
    if percentile == "avg":
        return np.mean(values)
    return np.percentile(values, percentile)


def get_cutoff_date(days: int | None) -> datetime | None:
    """Get cutoff date for time filtering."""
    if days:
        return datetime.utcnow() - timedelta(days=days)
    return None


def get_available_symbols() -> list[str]:
    """Get list of unique token symbols."""
    db = SessionLocal()
    try:
        symbols = (
            db.query(Token.symbol)
            .distinct()
            .filter(Token.symbol != UNKNOWN_SYMBOL)
            .order_by(Token.symbol)
            .all()
        )
        return [s[0] for s in symbols]
    finally:
        db.close()


def get_token_ids_for_symbol(db, symbol: str) -> list[int]:
    """Get all token IDs for a given symbol."""
    tokens = db.query(Token.id).filter_by(symbol=symbol).all()
    return [t[0] for t in tokens]


def get_chains_for_symbol(db, symbol: str) -> list[str]:
    """Get all chains where a token symbol is available."""
    chains = (
        db.query(Token.chain)
        .filter(Token.symbol == symbol, Token.chain.isnot(None))
        .distinct()
        .order_by(Token.chain)
        .all()
    )
    return [c[0] for c in chains]


def load_slippage_matrix(
    symbol: str, days: int = None, percentile_type: str = "avg"
) -> pd.DataFrame:
    """Load slippage matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=float)

        # Build chain -> token_id mapping for this symbol
        tokens = db.query(Token).filter_by(symbol=symbol).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

        cutoff_date = get_cutoff_date(days)

        for from_chain in chains:
            for to_chain in chains:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = SAME_CHAIN_SLIPPAGE
                else:
                    token_in_id = chain_to_token.get(from_chain)
                    token_out_id = chain_to_token.get(to_chain)

                    if token_in_id and token_out_id:
                        query = db.query(BridgeTransaction.slippage).filter(
                            BridgeTransaction.token_in_id == token_in_id,
                            BridgeTransaction.token_out_id == token_out_id,
                        )

                        if cutoff_date:
                            query = query.filter(
                                BridgeTransaction.created_at >= cutoff_date
                            )

                        slippages = [s[0] for s in query.all()]

                        if slippages:
                            result = calculate_percentile(slippages, percentile_type)
                            matrix.loc[from_chain, to_chain] = result
                        else:
                            matrix.loc[from_chain, to_chain] = np.nan
                    else:
                        matrix.loc[from_chain, to_chain] = np.nan

        return matrix

    finally:
        db.close()


def get_transaction_counts(symbol: str, days: int = None) -> pd.DataFrame:
    """Get transaction counts matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=int)

        tokens = db.query(Token).filter_by(symbol=symbol).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

        cutoff_date = get_cutoff_date(days)

        for from_chain in chains:
            for to_chain in chains:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = 0
                else:
                    token_in_id = chain_to_token.get(from_chain)
                    token_out_id = chain_to_token.get(to_chain)

                    if token_in_id and token_out_id:
                        query = db.query(func.count(BridgeTransaction.id)).filter(
                            BridgeTransaction.token_in_id == token_in_id,
                            BridgeTransaction.token_out_id == token_out_id,
                        )

                        if cutoff_date:
                            query = query.filter(
                                BridgeTransaction.created_at >= cutoff_date
                            )

                        count = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = count
                    else:
                        matrix.loc[from_chain, to_chain] = 0

        return matrix

    finally:
        db.close()


def get_volume_matrix(symbol: str, days: int = None) -> pd.DataFrame:
    """Get volume matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=float)

        tokens = db.query(Token).filter_by(symbol=symbol).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

        cutoff_date = get_cutoff_date(days)

        for from_chain in chains:
            for to_chain in chains:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = SAME_CHAIN_SLIPPAGE
                else:
                    token_in_id = chain_to_token.get(from_chain)
                    token_out_id = chain_to_token.get(to_chain)

                    if token_in_id and token_out_id:
                        query = db.query(
                            func.sum(BridgeTransaction.amount_in)
                        ).filter(
                            BridgeTransaction.token_in_id == token_in_id,
                            BridgeTransaction.token_out_id == token_out_id,
                        )

                        if cutoff_date:
                            query = query.filter(
                                BridgeTransaction.created_at >= cutoff_date
                            )

                        volume = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = volume
                    else:
                        matrix.loc[from_chain, to_chain] = 0

        return matrix

    finally:
        db.close()


def get_routes_data(days: int = None, percentile_type: str = "avg") -> pd.DataFrame:
    """Get all routes with their volume and slippage."""
    db = SessionLocal()

    try:
        cutoff_date = get_cutoff_date(days)

        query = db.query(
            BridgeTransaction.token_in_id, BridgeTransaction.token_out_id
        ).distinct()

        if cutoff_date:
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)

        pairs = query.all()

        routes = []
        for token_in_id, token_out_id in pairs:
            token_in = db.query(Token).filter_by(id=token_in_id).first()
            token_out = db.query(Token).filter_by(id=token_out_id).first()

            if not token_in or not token_out:
                continue

            tx_query = db.query(
                BridgeTransaction.slippage, BridgeTransaction.amount_in
            ).filter(
                BridgeTransaction.token_in_id == token_in_id,
                BridgeTransaction.token_out_id == token_out_id,
            )

            if cutoff_date:
                tx_query = tx_query.filter(
                    BridgeTransaction.created_at >= cutoff_date
                )

            transactions = tx_query.all()

            if not transactions:
                continue

            slippages = [tx[0] for tx in transactions]
            volumes = [tx[1] for tx in transactions]

            total_volume = sum(volumes)
            slippage_metric = calculate_percentile(slippages, percentile_type)
            tx_count = len(transactions)

            routes.append({
                "Source Token": token_in.symbol,
                "Source Chain": token_in.chain or NA_PLACEHOLDER,
                "Dest Token": token_out.symbol,
                "Dest Chain": token_out.chain or NA_PLACEHOLDER,
                "Volume": total_volume,
                "Slippage %": slippage_metric if slippage_metric is not None else 0,
                "Transactions": tx_count,
            })

        df = pd.DataFrame(routes)

        if not df.empty:
            df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

        return df

    finally:
        db.close()


def get_overall_stats(days: int = None) -> dict:
    """Get overall statistics with optional time filter."""
    db = SessionLocal()

    try:
        query = db.query(BridgeTransaction)

        if days:
            cutoff_date = get_cutoff_date(days)
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)

        total_txs = query.count()
        total_volume = (
            query.with_entities(func.sum(BridgeTransaction.amount_in)).scalar() or 0
        )

        if total_txs > 0:
            oldest = query.with_entities(
                func.min(BridgeTransaction.created_at)
            ).scalar()
            newest = query.with_entities(
                func.max(BridgeTransaction.created_at)
            ).scalar()
            date_range = f"{oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}"
        else:
            date_range = "No data"

        return {
            "transactions": total_txs,
            "volume": total_volume,
            "date_range": date_range,
        }
    finally:
        db.close()


def get_token_stats(symbol: str, days: int = None) -> dict:
    """Get statistics for a token symbol (aggregated across all chains)."""
    db = SessionLocal()

    try:
        token_ids = get_token_ids_for_symbol(db, symbol)
        if not token_ids:
            return {
                "transactions": 0,
                "volume": 0,
                "symbol": symbol,
            }

        query = db.query(BridgeTransaction).filter(
            (BridgeTransaction.token_in_id.in_(token_ids))
            | (BridgeTransaction.token_out_id.in_(token_ids))
        )

        if days:
            cutoff_date = get_cutoff_date(days)
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)

        total_txs = query.count()
        total_volume = (
            query.with_entities(func.sum(BridgeTransaction.amount_in)).scalar() or 0
        )

        return {
            "transactions": total_txs,
            "volume": total_volume,
            "symbol": symbol,
        }
    finally:
        db.close()
