import numpy as np
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import aliased
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


def _apply_date_filter(query, start_date: date | None, end_date: date | None):
    """Apply date range filter to a query."""
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(BridgeTransaction.created_at >= start_datetime)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(BridgeTransaction.created_at <= end_datetime)
    return query


def get_earliest_transaction_date() -> date | None:
    """Get the earliest transaction date from the database."""
    db = SessionLocal()
    try:
        result = db.query(func.min(BridgeTransaction.created_at)).scalar()
        if result:
            return result.date()
        return None
    finally:
        db.close()


def get_available_symbols() -> list[str]:
    """Get list of unique token symbols (case-insensitive grouping)."""
    db = SessionLocal()
    try:
        symbols = (
            db.query(Token.symbol)
            .filter(Token.symbol != UNKNOWN_SYMBOL)
            .all()
        )
        # Group symbols case-insensitively, keeping the uppercase version
        symbol_map = {}
        for (symbol,) in symbols:
            key = symbol.upper()
            if key not in symbol_map:
                symbol_map[key] = symbol.upper()
        return sorted(symbol_map.values())
    finally:
        db.close()


def get_token_ids_for_symbol(db, symbol: str) -> list[int]:
    """Get all token IDs for a given symbol (case-insensitive)."""
    tokens = db.query(Token.id).filter(
        func.upper(Token.symbol) == symbol.upper()
    ).all()
    return [t[0] for t in tokens]


def get_chains_for_symbol(db, symbol: str) -> list[str]:
    """Get all chains where a token symbol is available (case-insensitive)."""
    chains = (
        db.query(Token.chain)
        .filter(func.upper(Token.symbol) == symbol.upper(), Token.chain.isnot(None))
        .distinct()
        .order_by(Token.chain)
        .all()
    )
    return [c[0] for c in chains]


def load_slippage_matrix(
    symbol: str,
    start_date: date = None,
    end_date: date = None,
    percentile_type: str | int = "avg",
) -> pd.DataFrame:
    """Load slippage matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=float)

        # Build chain -> token_id mapping for this symbol (case-insensitive)
        tokens = db.query(Token).filter(
            func.upper(Token.symbol) == symbol.upper()
        ).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

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
                        query = _apply_date_filter(query, start_date, end_date)

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


def get_transaction_counts(
    symbol: str,
    start_date: date = None,
    end_date: date = None,
) -> pd.DataFrame:
    """Get transaction counts matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=int)

        tokens = db.query(Token).filter(
            func.upper(Token.symbol) == symbol.upper()
        ).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

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
                        query = _apply_date_filter(query, start_date, end_date)

                        count = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = count
                    else:
                        matrix.loc[from_chain, to_chain] = 0

        return matrix

    finally:
        db.close()


def get_volume_matrix(
    symbol: str,
    start_date: date = None,
    end_date: date = None,
) -> pd.DataFrame:
    """Get volume matrix for a token across all its available chains."""
    db = SessionLocal()

    try:
        chains = get_chains_for_symbol(db, symbol)
        if not chains:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=chains, columns=chains, dtype=float)

        tokens = db.query(Token).filter(
            func.upper(Token.symbol) == symbol.upper()
        ).all()
        chain_to_token = {t.chain: t.id for t in tokens if t.chain}

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
                        query = _apply_date_filter(query, start_date, end_date)

                        volume = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = volume
                    else:
                        matrix.loc[from_chain, to_chain] = 0

        return matrix

    finally:
        db.close()


def get_routes_data(
    start_date: date = None,
    end_date: date = None,
    min_amount: float = None,
    max_amount: float = None,
) -> pd.DataFrame:
    """Get all routes with their volume, average slippage, and avg tx size."""
    db = SessionLocal()

    try:
        # Create aliases for source and destination tokens
        token_in_alias = aliased(Token, name="token_in")
        token_out_alias = aliased(Token, name="token_out")

        # Use outer joins so transactions with missing token_in/token_out are still
        # included; otherwise routes total volume would be less than DB total.
        query = db.query(
            BridgeTransaction.token_in_id,
            BridgeTransaction.token_out_id,
            func.coalesce(token_in_alias.symbol, UNKNOWN_SYMBOL).label("source_token"),
            func.coalesce(token_in_alias.chain, NA_PLACEHOLDER).label("source_chain"),
            func.coalesce(token_out_alias.symbol, UNKNOWN_SYMBOL).label("dest_token"),
            func.coalesce(token_out_alias.chain, NA_PLACEHOLDER).label("dest_chain"),
            func.sum(BridgeTransaction.amount_in).label("volume"),
            func.avg(BridgeTransaction.slippage).label("avg_slippage"),
            func.count(BridgeTransaction.id).label("tx_count"),
            func.avg(BridgeTransaction.amount_in).label("avg_tx_size"),
        ).outerjoin(
            token_in_alias, BridgeTransaction.token_in_id == token_in_alias.id
        ).outerjoin(
            token_out_alias, BridgeTransaction.token_out_id == token_out_alias.id
        )

        # Apply date filter before grouping
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(BridgeTransaction.created_at >= start_datetime)
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(BridgeTransaction.created_at <= end_datetime)

        # Apply amount filter
        if min_amount is not None:
            query = query.filter(BridgeTransaction.amount_in >= min_amount)
        if max_amount is not None:
            query = query.filter(BridgeTransaction.amount_in < max_amount)

        query = query.group_by(
            BridgeTransaction.token_in_id,
            BridgeTransaction.token_out_id,
            func.coalesce(token_in_alias.symbol, UNKNOWN_SYMBOL),
            func.coalesce(token_in_alias.chain, NA_PLACEHOLDER),
            func.coalesce(token_out_alias.symbol, UNKNOWN_SYMBOL),
            func.coalesce(token_out_alias.chain, NA_PLACEHOLDER),
        )

        results = query.all()

        routes = []
        for row in results:
            slippage_value = row.avg_slippage if row.avg_slippage is not None else 0
            avg_tx_size = row.avg_tx_size if row.avg_tx_size is not None else 0

            routes.append({
                "Source Token": row.source_token,
                "Source Chain": row.source_chain or NA_PLACEHOLDER,
                "Dest Token": row.dest_token,
                "Dest Chain": row.dest_chain or NA_PLACEHOLDER,
                "Volume": row.volume or 0,
                "Slippage %": slippage_value,
                "Transactions": row.tx_count,
                "Avg Tx Size": avg_tx_size,
            })

        df = pd.DataFrame(routes)

        if not df.empty:
            df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

        return df

    finally:
        db.close()


def get_overall_stats(start_date: date = None, end_date: date = None) -> dict:
    """Get overall statistics with optional date range filter."""
    db = SessionLocal()

    try:
        query = db.query(BridgeTransaction)
        query = _apply_date_filter(query, start_date, end_date)

        total_txs = query.count()
        total_volume = (
            query.with_entities(func.sum(BridgeTransaction.amount_in)).scalar() or 0
        )

        return {
            "transactions": total_txs,
            "volume": total_volume,
        }
    finally:
        db.close()


def get_token_stats(
    symbol: str,
    start_date: date = None,
    end_date: date = None,
) -> dict:
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
        query = _apply_date_filter(query, start_date, end_date)

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


def get_token_daily_stats(
    symbol: str,
    start_date: date = None,
    end_date: date = None,
) -> pd.DataFrame:
    """Get daily volume and transaction counts for a token."""
    db = SessionLocal()

    try:
        token_ids = get_token_ids_for_symbol(db, symbol)
        if not token_ids:
            return pd.DataFrame()

        # Query with date truncation for daily grouping
        query = db.query(
            func.date_trunc('day', BridgeTransaction.created_at).label('date'),
            func.sum(BridgeTransaction.amount_in).label('volume'),
            func.count(BridgeTransaction.id).label('transactions'),
        ).filter(
            (BridgeTransaction.token_in_id.in_(token_ids))
            | (BridgeTransaction.token_out_id.in_(token_ids))
        )

        query = _apply_date_filter(query, start_date, end_date)

        query = query.group_by(
            func.date_trunc('day', BridgeTransaction.created_at)
        ).order_by(
            func.date_trunc('day', BridgeTransaction.created_at)
        )

        results = query.all()

        if not results:
            return pd.DataFrame()

        data = []
        for row in results:
            data.append({
                "Date": row.date.date() if row.date else None,
                "Volume": row.volume or 0,
                "Transactions": row.transactions or 0,
            })

        df = pd.DataFrame(data)
        return df

    finally:
        db.close()


def get_route_daily_stats(
    source_token: str,
    source_chain: str,
    dest_token: str,
    dest_chain: str,
    start_date: date = None,
    end_date: date = None,
) -> pd.DataFrame:
    """Get daily volume and transaction counts for a specific route."""
    db = SessionLocal()

    try:
        # Find source token ID
        source_token_obj = db.query(Token).filter(
            func.upper(Token.symbol) == source_token.upper(),
            Token.chain == source_chain,
        ).first()

        # Find dest token ID
        dest_token_obj = db.query(Token).filter(
            func.upper(Token.symbol) == dest_token.upper(),
            Token.chain == dest_chain,
        ).first()

        if not source_token_obj or not dest_token_obj:
            return pd.DataFrame()

        # Query with date truncation for daily grouping
        query = db.query(
            func.date_trunc('day', BridgeTransaction.created_at).label('date'),
            func.sum(BridgeTransaction.amount_in).label('volume'),
            func.count(BridgeTransaction.id).label('transactions'),
        ).filter(
            BridgeTransaction.token_in_id == source_token_obj.id,
            BridgeTransaction.token_out_id == dest_token_obj.id,
        )

        query = _apply_date_filter(query, start_date, end_date)

        query = query.group_by(
            func.date_trunc('day', BridgeTransaction.created_at)
        ).order_by(
            func.date_trunc('day', BridgeTransaction.created_at)
        )

        results = query.all()

        if not results:
            return pd.DataFrame()

        data = []
        for row in results:
            data.append({
                "Date": row.date.date() if row.date else None,
                "Volume": row.volume or 0,
                "Transactions": row.transactions or 0,
            })

        return pd.DataFrame(data)

    finally:
        db.close()


def get_route_slippage_percentile(
    source_token: str,
    source_chain: str,
    dest_token: str,
    dest_chain: str,
    percentile_type: str | int,
    start_date: date = None,
    end_date: date = None,
) -> float | None:
    """Get slippage percentile for a specific route."""
    db = SessionLocal()

    try:
        # Find source token ID
        source_token_obj = db.query(Token).filter(
            func.upper(Token.symbol) == source_token.upper(),
            Token.chain == source_chain,
        ).first()

        # Find dest token ID
        dest_token_obj = db.query(Token).filter(
            func.upper(Token.symbol) == dest_token.upper(),
            Token.chain == dest_chain,
        ).first()

        if not source_token_obj or not dest_token_obj:
            return None

        # Query slippage values
        query = db.query(BridgeTransaction.slippage).filter(
            BridgeTransaction.token_in_id == source_token_obj.id,
            BridgeTransaction.token_out_id == dest_token_obj.id,
        )

        query = _apply_date_filter(query, start_date, end_date)

        slippages = [s[0] for s in query.all() if s[0] is not None]

        if not slippages:
            return None

        return calculate_percentile(slippages, percentile_type)

    finally:
        db.close()
