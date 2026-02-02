import streamlit as st
import pandas as pd
import numpy as np
from database import SessionLocal, Token, BridgeTransaction, init_db
from datetime import datetime, timedelta
from sqlalchemy import func

CHAINS = ["eth", "arb", "base", "op", "polygon", "bsc", "avax", "sol"]

# Time period options
TIME_PERIODS = {
    "1 Day": 1,
    "7 Days": 7,
    "30 Days": 30,
    "All Time": None
}

# Percentile options
PERCENTILE_OPTIONS = {
    "Average": "avg",
    "Median (P50)": 50,
    "P25": 25,
    "P75": 75,
    "P95": 95,
    "P99": 99
}

def calculate_percentile(values, percentile):
    """Calculate percentile from list of values"""
    if not values:
        return None
    if percentile == "avg":
        return np.mean(values)
    return np.percentile(values, percentile)

@st.cache_data(ttl=60)
def get_available_tokens() -> list:
    """Get list of all tokens with their details"""
    db = SessionLocal()
    try:
        # Get all tokens, ordered by symbol (known tokens first), then by chain
        tokens = db.query(Token).order_by(
            Token.symbol == "UNKNOWN",  # Known tokens first (False=0 comes before True=1)
            Token.symbol,
            Token.chain
        ).all()
        return [(t.id, t.symbol, t.chain, t.asset_id) for t in tokens]
    finally:
        db.close()

@st.cache_data(ttl=60)
def load_slippage_matrix(token_id: int, days: int = None, percentile_type: str = "avg") -> pd.DataFrame:
    """Load slippage matrix with time and percentile filters"""
    db = SessionLocal()
    
    try:
        matrix = pd.DataFrame(index=CHAINS, columns=CHAINS, dtype=float)
        
        # Get the selected token
        selected_token = db.query(Token).filter_by(id=token_id).first()
        if not selected_token:
            return matrix
        
        # Get all tokens with the same symbol
        tokens = db.query(Token).filter_by(symbol=selected_token.symbol).all()
        token_map = {t.chain: t for t in tokens}
        
        # Calculate cutoff date if time filter is applied
        cutoff_date = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        for from_chain in CHAINS:
            for to_chain in CHAINS:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = 0.0
                else:
                    # Get token IDs for this chain pair
                    token_in = token_map.get(from_chain)
                    token_out = token_map.get(to_chain)
                    
                    if token_in and token_out:
                        # Query transactions directly
                        query = db.query(BridgeTransaction.slippage).filter(
                            BridgeTransaction.token_in_id == token_in.id,
                            BridgeTransaction.token_out_id == token_out.id
                        )
                        
                        # Apply time filter
                        if cutoff_date:
                            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
                        
                        # Get all slippage values
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

@st.cache_data(ttl=60)
def get_transaction_counts(token_id: int, days: int = None) -> pd.DataFrame:
    """Get transaction counts with time filter"""
    db = SessionLocal()
    
    try:
        matrix = pd.DataFrame(index=CHAINS, columns=CHAINS, dtype=int)
        
        # Get the selected token
        selected_token = db.query(Token).filter_by(id=token_id).first()
        if not selected_token:
            return matrix
        
        # Get all tokens for this symbol
        tokens = db.query(Token).filter_by(symbol=selected_token.symbol).all()
        token_map = {t.chain: t for t in tokens}
        
        # Calculate cutoff date if time filter is applied
        cutoff_date = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        for from_chain in CHAINS:
            for to_chain in CHAINS:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = 0
                else:
                    token_in = token_map.get(from_chain)
                    token_out = token_map.get(to_chain)
                    
                    if token_in and token_out:
                        query = db.query(func.count(BridgeTransaction.id)).filter(
                            BridgeTransaction.token_in_id == token_in.id,
                            BridgeTransaction.token_out_id == token_out.id
                        )
                        
                        # Apply time filter
                        if cutoff_date:
                            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
                        
                        count = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = count
                    else:
                        matrix.loc[from_chain, to_chain] = 0
        
        return matrix
    
    finally:
        db.close()

@st.cache_data(ttl=60)
def get_volume_matrix(token_id: int, days: int = None) -> pd.DataFrame:
    """Get total volume by route"""
    db = SessionLocal()
    
    try:
        matrix = pd.DataFrame(index=CHAINS, columns=CHAINS, dtype=float)
        
        # Get the selected token
        selected_token = db.query(Token).filter_by(id=token_id).first()
        if not selected_token:
            return matrix
        
        # Get all tokens for this symbol
        tokens = db.query(Token).filter_by(symbol=selected_token.symbol).all()
        token_map = {t.chain: t for t in tokens}
        
        # Calculate cutoff date if time filter is applied
        cutoff_date = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        for from_chain in CHAINS:
            for to_chain in CHAINS:
                if from_chain == to_chain:
                    matrix.loc[from_chain, to_chain] = 0.0
                else:
                    token_in = token_map.get(from_chain)
                    token_out = token_map.get(to_chain)
                    
                    if token_in and token_out:
                        query = db.query(func.sum(BridgeTransaction.amount_in)).filter(
                            BridgeTransaction.token_in_id == token_in.id,
                            BridgeTransaction.token_out_id == token_out.id
                        )
                        
                        # Apply time filter
                        if cutoff_date:
                            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
                        
                        volume = query.scalar() or 0
                        matrix.loc[from_chain, to_chain] = volume
                    else:
                        matrix.loc[from_chain, to_chain] = 0
        
        return matrix
    
    finally:
        db.close()

@st.cache_data(ttl=60)
def get_routes_data(days: int = None, percentile_type: str = "avg") -> pd.DataFrame:
    """Get all routes with their volume and slippage"""
    db = SessionLocal()
    
    try:
        # Calculate cutoff date if time filter is applied
        cutoff_date = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query all distinct token pairs with transactions
        query = db.query(
            BridgeTransaction.token_in_id,
            BridgeTransaction.token_out_id
        ).distinct()
        
        if cutoff_date:
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
        
        pairs = query.all()
        
        routes = []
        for token_in_id, token_out_id in pairs:
            # Get token info
            token_in = db.query(Token).filter_by(id=token_in_id).first()
            token_out = db.query(Token).filter_by(id=token_out_id).first()
            
            if not token_in or not token_out:
                continue
            
            # Get transactions for this pair
            tx_query = db.query(
                BridgeTransaction.slippage,
                BridgeTransaction.amount_in
            ).filter(
                BridgeTransaction.token_in_id == token_in_id,
                BridgeTransaction.token_out_id == token_out_id
            )
            
            if cutoff_date:
                tx_query = tx_query.filter(BridgeTransaction.created_at >= cutoff_date)
            
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
                "Source Chain": token_in.chain or "N/A",
                "Dest Token": token_out.symbol,
                "Dest Chain": token_out.chain or "N/A",
                "Volume": total_volume,
                "Slippage %": slippage_metric if slippage_metric is not None else 0,
                "Transactions": tx_count
            })
        
        df = pd.DataFrame(routes)
        
        if not df.empty:
            # Sort by volume descending
            df = df.sort_values("Volume", ascending=False).reset_index(drop=True)
        
        return df
    
    finally:
        db.close()

@st.cache_data(ttl=300)
def get_stats(days: int = None):
    """Get overall statistics with optional time filter"""
    db = SessionLocal()
    
    try:
        query = db.query(BridgeTransaction)
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
        
        total_txs = query.count()
        total_volume = query.with_entities(func.sum(BridgeTransaction.amount_in)).scalar() or 0
        
        # Get date range
        if total_txs > 0:
            oldest = query.with_entities(func.min(BridgeTransaction.created_at)).scalar()
            newest = query.with_entities(func.max(BridgeTransaction.created_at)).scalar()
            date_range = f"{oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}"
        else:
            date_range = "No data"
        
        return {
            "transactions": total_txs,
            "volume": total_volume,
            "date_range": date_range
        }
    finally:
        db.close()

@st.cache_data(ttl=300)
def get_token_stats(token_id: int, days: int = None):
    """Get statistics for a specific token (by asset ID)"""
    db = SessionLocal()
    
    try:
        # Get the selected token
        selected_token = db.query(Token).filter_by(id=token_id).first()
        if not selected_token:
            return {"transactions": 0, "volume": 0, "symbol": "N/A", "chain": "N/A"}
        
        # Query transactions involving this specific token
        query = db.query(BridgeTransaction).filter(
            (BridgeTransaction.token_in_id == token_id) | 
            (BridgeTransaction.token_out_id == token_id)
        )
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(BridgeTransaction.created_at >= cutoff_date)
        
        total_txs = query.count()
        total_volume = query.with_entities(func.sum(BridgeTransaction.amount_in)).scalar() or 0
        
        return {
            "transactions": total_txs,
            "volume": total_volume,
            "symbol": selected_token.symbol,
            "chain": selected_token.chain or "N/A"
        }
    finally:
        db.close()

# ============================================================================
# MAIN UI
# ============================================================================

# Page config
st.set_page_config(page_title="Stablecoin Bridge Analytics", layout="wide")
st.title("🌉 Stablecoin Bridge Analytics")
st.markdown("### Cross-Chain Bridging Analysis Dashboard")

init_db()

# Get available tokens
available_tokens = get_available_tokens()
if not available_tokens:
    st.error("No tokens found in database. Please run the collector first.")
    st.stop()

# Create display labels for tokens: "USDT (eth) - nep141:eth-0x..."
token_display_map = {}
token_id_map = {}
for token_id, symbol, chain, asset_id in available_tokens:
    # Show more detail for unknown tokens
    if symbol == "UNKNOWN":
        display_label = f"{asset_id[:70]}..." if len(asset_id) > 70 else asset_id
    else:
        display_label = f"{symbol} ({chain or 'N/A'}) - {asset_id[:50]}..."
    token_display_map[display_label] = token_id
    token_id_map[token_id] = (symbol, chain, asset_id)

# Main tabs
main_tab1, main_tab2 = st.tabs(["📊 Per Token Analysis", "🔀 Routes Analysis"])

# ============================================================================
# TAB 1: PER TOKEN ANALYSIS
# ============================================================================
with main_tab1:
    st.header("Per Token Analysis")
    
    # Filters in columns
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([2, 2, 2, 1])
    
    with col_filter1:
        selected_token_display = st.selectbox("🪙 Select Asset:", list(token_display_map.keys()), key="token_tab1")
        selected_token_id = token_display_map[selected_token_display]
    
    with col_filter2:
        selected_period = st.selectbox(
            "📅 Time Period:",
            list(TIME_PERIODS.keys()),
            index=3,  # Default to "All Time"
            key="period_tab1"
        )
        days_filter = TIME_PERIODS[selected_period]
    
    with col_filter3:
        selected_percentile_label = st.selectbox(
            "📊 Slippage Metric:",
            list(PERCENTILE_OPTIONS.keys()),
            index=0,  # Default to "Average"
            key="percentile_tab1"
        )
        percentile_value = PERCENTILE_OPTIONS[selected_percentile_label]
    
    with col_filter4:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_tab1"):
            st.cache_data.clear()
            st.rerun()
    
    # Token stats
    token_stats = get_token_stats(selected_token_id, days_filter)
    token_symbol = token_stats.get('symbol', 'N/A')
    token_chain = token_stats.get('chain', 'N/A')
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric(f"{token_symbol} ({token_chain}) Transactions", f"{token_stats['transactions']:,}")
    with col_stat2:
        st.metric(f"{token_symbol} ({token_chain}) Volume", f"${token_stats['volume']:,.0f}")
    with col_stat3:
        st.metric("Period", selected_period)
    
    st.markdown("---")
    
    # Slippage Matrix
    st.subheader(f"Slippage Matrix (%) - {selected_percentile_label}")
    slippage_matrix = load_slippage_matrix(selected_token_id, days_filter, percentile_value)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            slippage_matrix.style.format("{:.4f}", na_rep="N/A").background_gradient(
                cmap="RdYlGn_r", axis=None, vmin=0, vmax=1
            ), 
            height=300
        )
    
    with col2:
        st.markdown("**How to read:**")
        st.markdown("- **Row** = From Chain")
        st.markdown("- **Column** = To Chain")
        st.markdown(f"- **Value** = {selected_percentile_label} Slippage %")
        st.markdown("- 🟢 Green = Low slippage (good)")
        st.markdown("- 🔴 Red = High slippage (bad)")
    
    st.markdown("---")
    
    # Transaction Counts and Volume in sub-tabs
    sub_tab1, sub_tab2 = st.tabs(["📈 Transaction Counts", "💰 Volume"])
    
    with sub_tab1:
        tx_counts = get_transaction_counts(selected_token_id, days_filter)
        
        st.dataframe(
            tx_counts.style.format("{:,}").background_gradient(
                cmap="Blues", axis=None
            ),
            height=300
        )
    
    with sub_tab2:
        volume_matrix = get_volume_matrix(selected_token_id, days_filter)
        
        st.dataframe(
            volume_matrix.style.format("${:,.0f}").background_gradient(
                cmap="Greens", axis=None
            ),
            height=300
        )

# ============================================================================
# TAB 2: ROUTES ANALYSIS
# ============================================================================
with main_tab2:
    st.header("Routes Analysis")
    
    # Filters in columns
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
    
    with col_filter1:
        selected_period_routes = st.selectbox(
            "📅 Time Period:",
            list(TIME_PERIODS.keys()),
            index=3,  # Default to "All Time"
            key="period_tab2"
        )
        days_filter_routes = TIME_PERIODS[selected_period_routes]
    
    with col_filter2:
        selected_percentile_routes = st.selectbox(
            "📊 Slippage Metric:",
            list(PERCENTILE_OPTIONS.keys()),
            index=0,  # Default to "Average"
            key="percentile_tab2"
        )
        percentile_value_routes = PERCENTILE_OPTIONS[selected_percentile_routes]
    
    with col_filter3:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_tab2"):
            st.cache_data.clear()
            st.rerun()
    
    # Overall stats
    overall_stats = get_stats(days_filter_routes)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Transactions", f"{overall_stats['transactions']:,}")
    with col_stat2:
        st.metric("Total Volume", f"${overall_stats['volume']:,.0f}")
    with col_stat3:
        st.metric("Period", selected_period_routes)
    
    st.markdown("---")
    
    # Routes table
    st.subheader(f"All Routes - {selected_percentile_routes} Slippage")
    routes_df = get_routes_data(days_filter_routes, percentile_value_routes)
    
    if routes_df.empty:
        st.warning("No routes found for the selected period.")
    else:
        # Format the dataframe for display
        display_df = routes_df.copy()
        
        # Add a route column for easier reading
        display_df.insert(0, "Route", 
            display_df["Source Token"] + " (" + display_df["Source Chain"] + ") → " + 
            display_df["Dest Token"] + " (" + display_df["Dest Chain"] + ")"
        )
        
        # Display with formatting
        st.dataframe(
            display_df.style.format({
                "Volume": "${:,.0f}",
                "Slippage %": "{:.4f}",
                "Transactions": "{:,}"
            }).background_gradient(
                subset=["Slippage %"],
                cmap="RdYlGn_r",
                vmin=0,
                vmax=display_df["Slippage %"].max() if not display_df.empty else 1
            ).background_gradient(
                subset=["Volume"],
                cmap="Greens"
            ),
            height=600,
            use_container_width=True
        )
        
        # Summary metrics below table
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Routes", len(routes_df))
        
        with col2:
            avg_slippage = routes_df["Slippage %"].mean()
            st.metric("Average Slippage", f"{avg_slippage:.4f}%")
        
        with col3:
            total_route_volume = routes_df["Volume"].sum()
            st.metric("Total Volume", f"${total_route_volume:,.0f}")

# Footer
st.markdown("---")
st.caption("**Slippage Formula:** (Amount In - Amount Out) / Amount In × 100%")
st.caption("💡 Data is cached for 1 minute. Use Refresh button to force update.")
