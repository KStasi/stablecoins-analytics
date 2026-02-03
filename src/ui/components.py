import streamlit as st
import pandas as pd
from datetime import date, timedelta
from src.const import (
    MATRIX_TABLE_HEIGHT,
    ROUTES_TABLE_HEIGHT,
    DECIMAL_PLACES,
    NA_PLACEHOLDER,
    STABLECOINS,
    TRANSACTION_SIZE_FILTERS,
    USDC_ZERO_FEE_ROUTES,
    USDT_NATIVE_ZERO_FEE_ROUTES,
    USDT0_ZERO_FEE_ROUTES,
)


# =============================================================================
# CHAIN NAME NORMALIZATION
# Maps database chain names (various cases/abbreviations) to canonical names
# used in zero-fee route definitions
# =============================================================================
CHAIN_NAME_MAPPING = {
    # Ethereum variants
    "eth": "Ethereum",
    "ETH": "Ethereum",
    "ethereum": "Ethereum",
    "Ethereum": "Ethereum",
    # Optimism variants
    "op": "OP Mainnet",
    "OP": "OP Mainnet",
    "optimism": "OP Mainnet",
    "Optimism": "OP Mainnet",
    # Arbitrum variants
    "arb": "Arbitrum One",
    "ARB": "Arbitrum One",
    "arbitrum": "Arbitrum One",
    "Arbitrum": "Arbitrum One",
    "Arbitrum One": "Arbitrum One",
    # Base variants
    "base": "Base",
    "BASE": "Base",
    "Base": "Base",
    # Polygon variants
    "polygon": "Polygon",
    "POLYGON": "Polygon",
    "Polygon": "Polygon",
    "matic": "Polygon",
    "MATIC": "Polygon",
    # BNB/BSC variants
    "bnb": "BNB",
    "BNB": "BNB",
    "bsc": "BNB",
    "BSC": "BNB",
    # Avalanche variants
    "avax": "Avalanche",
    "AVAX": "Avalanche",
    "avalanche": "Avalanche",
    "Avalanche": "Avalanche",
    # Solana variants
    "sol": "Solana",
    "SOL": "Solana",
    "solana": "Solana",
    "Solana": "Solana",
    # Berachain variants
    "bera": "Berachain",
    "BERA": "Berachain",
    "berachain": "Berachain",
    "BERACHAIN": "Berachain",
    "Berachain": "Berachain",
    # Gnosis/xDAI variants
    "gnosis": "Gnosis",
    "GNOSIS": "Gnosis",
    "Gnosis": "Gnosis",
    "xdai": "Gnosis",
    "XDAI": "Gnosis",
    "xDAI": "Gnosis",
    # NEAR variants
    "near": "NEAR",
    "NEAR": "NEAR",
    "Near": "NEAR",
    # Tron variants
    "tron": "Tron",
    "TRON": "Tron",
    "Tron": "Tron",
    # Bitcoin variants
    "btc": "Bitcoin",
    "BTC": "Bitcoin",
    "bitcoin": "Bitcoin",
    "Bitcoin": "Bitcoin",
    # Litecoin variants
    "ltc": "Litecoin",
    "LTC": "Litecoin",
    # XRP variants
    "xrp": "XRP",
    "XRP": "XRP",
    # Dogecoin variants
    "doge": "Dogecoin",
    "DOGE": "Dogecoin",
    # Aptos variants
    "aptos": "Aptos",
    "APTOS": "Aptos",
    "Aptos": "Aptos",
    # Sui variants
    "sui": "Sui",
    "SUI": "Sui",
    "Sui": "Sui",
    # Starknet variants
    "starknet": "Starknet",
    "STARKNET": "Starknet",
    "Starknet": "Starknet",
    # X Layer variants
    "xlayer": "X Layer",
    "XLAYER": "X Layer",
    "X Layer": "X Layer",
    # Velas variants
    "velas": "Velas",
    "VELAS": "Velas",
    "Velas": "Velas",
    # Rari variants
    "rari": "Rari",
    "RARI": "Rari",
    "Rari": "Rari",
    # Bitcoin Cash variants
    "bch": "Bitcoin Cash",
    "BCH": "Bitcoin Cash",
    # Zcash variants
    "zec": "Zcash",
    "ZEC": "Zcash",
    # Cardano variants
    "cardano": "Cardano",
    "CARDANO": "Cardano",
    "Cardano": "Cardano",
    "ada": "Cardano",
    "ADA": "Cardano",
    # Ink variants
    "ink": "Ink",
    "INK": "Ink",
    "Ink": "Ink",
    # Linea variants
    "linea": "Linea Mainnet",
    "LINEA": "Linea Mainnet",
    "Linea": "Linea Mainnet",
    "Linea Mainnet": "Linea Mainnet",
    # Celo variants
    "celo": "Celo",
    "CELO": "Celo",
    "Celo": "Celo",
    # Mantle variants
    "mantle": "Mantle",
    "MANTLE": "Mantle",
    "Mantle": "Mantle",
    # Metis variants
    "metis": "Metis",
    "METIS": "Metis",
    "Metis": "Metis",
    # Sonic variants
    "sonic": "Sonic",
    "SONIC": "Sonic",
    "Sonic": "Sonic",
    # Fraxtal variants
    "fraxtal": "Fraxtal",
    "FRAXTAL": "Fraxtal",
    "Fraxtal": "Fraxtal",
    # Mode variants
    "mode": "Mode Mainnet",
    "MODE": "Mode Mainnet",
    "Mode": "Mode Mainnet",
    "Mode Mainnet": "Mode Mainnet",
    # Unichain variants
    "unichain": "Unichain",
    "UNICHAIN": "Unichain",
    "Unichain": "Unichain",
    # Sei variants
    "sei": "Sei Network",
    "SEI": "Sei Network",
    "Sei": "Sei Network",
    "Sei Network": "Sei Network",
    # Flare variants
    "flare": "Flare Mainnet",
    "FLARE": "Flare Mainnet",
    "Flare": "Flare Mainnet",
    "Flare Mainnet": "Flare Mainnet",
    # Rootstock variants
    "rootstock": "Rootstock",
    "ROOTSTOCK": "Rootstock",
    "Rootstock": "Rootstock",
    "rsk": "Rootstock",
    "RSK": "Rootstock",
    # Corn variants
    "corn": "Corn",
    "CORN": "Corn",
    "Corn": "Corn",
    # Plasma variants
    "plasma": "Plasma",
    "PLASMA": "Plasma",
    "Plasma": "Plasma",
    # HyperEVM variants
    "hyperevm": "HyperEVM",
    "HYPEREVM": "HyperEVM",
    "HyperEVM": "HyperEVM",
    # Swellchain variants
    "swellchain": "Swellchain",
    "SWELLCHAIN": "Swellchain",
    "Swellchain": "Swellchain",
    "swell": "Swellchain",
    "SWELL": "Swellchain",
    # Lisk variants
    "lisk": "Lisk",
    "LISK": "Lisk",
    "Lisk": "Lisk",
    # Soneium variants
    "soneium": "Soneium",
    "SONEIUM": "Soneium",
    "Soneium": "Soneium",
    # Ronin variants
    "ronin": "Ronin",
    "RONIN": "Ronin",
    "Ronin": "Ronin",
    # Superseed variants
    "superseed": "Superseed",
    "SUPERSEED": "Superseed",
    "Superseed": "Superseed",
    # BOB variants
    "bob": "BOB",
    "BOB": "BOB",
}


def normalize_chain_name(chain_name: str) -> str:
    """Normalize chain name from database format to canonical format.
    
    This function handles the various naming conventions used in the database
    (e.g., 'eth', 'ETH', 'arb', 'OP', 'POLYGON', 'bera', 'BERACHAIN') and 
    converts them to the canonical names used in zero-fee route definitions
    (e.g., 'Ethereum', 'Arbitrum One', 'OP Mainnet', 'Polygon', 'Berachain').
    
    Args:
        chain_name: The chain name as stored in the database
        
    Returns:
        The canonical chain name, or the original name if no mapping exists
    """
    if not chain_name:
        return chain_name
    return CHAIN_NAME_MAPPING.get(chain_name, chain_name)


def render_symbol_selector(symbols: list[str], key: str) -> str:
    """Render symbol selector and return selected symbol."""
    return st.selectbox("Select Token:", symbols, key=key)


def render_date_range_selector(key: str, earliest_date: date | None = None) -> tuple[date, date]:
    """Render date range selector and return (start_date, end_date)."""
    today = date.today()
    default_start = earliest_date if earliest_date else today - timedelta(days=30)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            max_value=today,
            key=f"{key}_start",
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=today,
            max_value=today,
            key=f"{key}_end",
        )

    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    return start_date, end_date


def render_percentile_slider(key: str) -> int | str:
    """Render percentile slider and return percentile value.

    Returns 'avg' for 0, otherwise returns the percentile (1-99).
    """
    value = st.slider(
        "Percentile",
        min_value=0,
        max_value=99,
        value=50,
        key=key,
        help="0 = Average, 1-99 = Percentile (e.g., 50 = Median)",
    )
    return "avg" if value == 0 else value


def render_stablecoin_filter(key: str) -> str:
    """Render stablecoin filter selector."""
    options = ["All Routes", "Stablecoins Only", "Include Stablecoins"]
    return st.selectbox(
        "Route Filter:",
        options,
        key=key,
        help="All Routes: Show all routes. Stablecoins Only: Both tokens are stablecoins. Include Stablecoins: At least one token is a stablecoin.",
    )


def render_transaction_size_filter(key: str) -> tuple[float | None, float | None]:
    """Render transaction size filter selector."""
    selected = st.selectbox(
        "Transaction Size:",
        list(TRANSACTION_SIZE_FILTERS.keys()),
        key=key,
        help="Filter routes by transaction amount range",
    )
    return TRANSACTION_SIZE_FILTERS[selected]


def get_percentile_label(percentile: int | str) -> str:
    """Get display label for percentile value."""
    if percentile == "avg" or percentile == 0:
        return "Average"
    elif percentile == 50:
        return "Median (P50)"
    else:
        return f"P{percentile}"


def render_refresh_button(key: str) -> bool:
    """Render refresh button and return if clicked."""
    return st.button("Refresh", use_container_width=True, key=key)


def render_stats_row(stats: dict) -> None:
    """Render a row of statistics metrics."""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Transactions", f"{stats['transactions']:,}")
    with col2:
        st.metric("Total Volume", f"${stats['volume']:,.0f}")


def render_token_stats_row(stats: dict) -> None:
    """Render a row of token-specific statistics."""
    symbol = stats.get("symbol", NA_PLACEHOLDER)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"{symbol} Transactions", f"{stats['transactions']:,}")
    with col2:
        st.metric(f"{symbol} Volume", f"${stats['volume']:,.0f}")


def render_slippage_matrix(matrix: pd.DataFrame, percentile_label: str) -> None:
    """Render slippage matrix with formatting and % sign."""
    if matrix.empty:
        st.warning("No data available for this token.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            matrix.style.format(
                lambda x: f"{x:.{DECIMAL_PLACES}f}%" if pd.notna(x) else NA_PLACEHOLDER
            ).background_gradient(cmap="RdYlGn_r", axis=None, vmin=0, vmax=1),
            height=MATRIX_TABLE_HEIGHT,
        )

    with col2:
        st.markdown("**How to read:**")
        st.markdown("- **Row** = From Chain")
        st.markdown("- **Column** = To Chain")
        st.markdown(f"- **Value** = {percentile_label} Slippage %")
        st.markdown("- Green = Low slippage (good)")
        st.markdown("- Red = High slippage (bad)")


def render_transaction_counts_matrix(matrix: pd.DataFrame) -> None:
    """Render transaction counts matrix."""
    if matrix.empty:
        st.warning("No data available for this token.")
        return

    st.dataframe(
        matrix.style.format("{:,}").background_gradient(cmap="Blues", axis=None),
        height=MATRIX_TABLE_HEIGHT,
    )


def render_volume_matrix(matrix: pd.DataFrame) -> None:
    """Render volume matrix."""
    if matrix.empty:
        st.warning("No data available for this token.")
        return

    st.dataframe(
        matrix.style.format("${:,.0f}").background_gradient(cmap="Greens", axis=None),
        height=MATRIX_TABLE_HEIGHT,
    )


def _is_stablecoin(symbol: str) -> bool:
    """Check if a symbol is a stablecoin (case-insensitive)."""
    return symbol.upper() in STABLECOINS


def filter_routes_by_stablecoin(df: pd.DataFrame, filter_type: str) -> pd.DataFrame:
    """Filter routes DataFrame based on stablecoin filter type."""
    if df.empty or filter_type == "All Routes":
        return df

    df = df.copy()

    if filter_type == "Stablecoins Only":
        # Both source and dest are stablecoins
        mask = df["Source Token"].apply(_is_stablecoin) & df["Dest Token"].apply(_is_stablecoin)
    elif filter_type == "Include Stablecoins":
        # At least one is a stablecoin
        mask = df["Source Token"].apply(_is_stablecoin) | df["Dest Token"].apply(_is_stablecoin)
    else:
        return df

    return df[mask].reset_index(drop=True)


def render_routes_stats(df: pd.DataFrame) -> None:
    """Render routes statistics metrics."""
    if df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Routes", 0)
        with col2:
            st.metric("Total Transactions", 0)
        with col3:
            st.metric("Average Slippage", "N/A")
        with col4:
            st.metric("Total Volume", "$0")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Routes", len(df))

    with col2:
        total_transactions = df["Transactions"].sum()
        st.metric("Total Transactions", f"{total_transactions:,}")

    with col3:
        avg_slippage = df["Slippage %"].mean()
        st.metric("Average Slippage", f"{avg_slippage:.{DECIMAL_PLACES}f}%")

    with col4:
        total_volume = df["Volume"].sum()
        st.metric("Total Volume", f"${total_volume:,.0f}")


def _normalize_token_symbol(symbol: str) -> str:
    """Normalize token symbol for comparison.
    
    Handles variants like USDT, USDt, USDT0, USDT.E -> USDT
    and USDC variants.
    """
    if not symbol:
        return ""
    upper = symbol.upper()
    # Normalize USDT variants
    if upper in ("USDT", "USDT0", "USDT.E", "USDTE"):
        return "USDT"
    return upper


def _tokens_match_for_zero_fee(source_token: str, dest_token: str) -> bool:
    """Check if source and destination tokens are the same (for zero-fee eligibility).
    
    Zero-fee bridging requires the same token on both ends (e.g., USDC -> USDC).
    """
    normalized_source = _normalize_token_symbol(source_token)
    normalized_dest = _normalize_token_symbol(dest_token)
    return normalized_source == normalized_dest


def _get_zero_fee_status(source_chain: str, dest_chain: str, source_token: str, dest_token: str) -> str:
    """Check if a zero-fee route exists for the given chain pair and tokens.

    Returns:
        - "✓" if zero-fee route exists
        - "" if no zero-fee route
        
    Note: Zero-fee bridging requires the same token on both source and destination.
    """
    # First check if tokens match - zero-fee only applies to same-token transfers
    if not _tokens_match_for_zero_fee(source_token, dest_token):
        return ""
    
    token_upper = _normalize_token_symbol(source_token)

    # Build lookup sets for each token type
    usdc_routes = set(USDC_ZERO_FEE_ROUTES)
    usdt_native_routes = set(USDT_NATIVE_ZERO_FEE_ROUTES)
    usdt0_routes = set(USDT0_ZERO_FEE_ROUTES)

    # Normalize chain names from database format to canonical format
    normalized_source = normalize_chain_name(source_chain)
    normalized_dest = normalize_chain_name(dest_chain)
    route_pair = (normalized_source, normalized_dest)

    # Check based on token type
    if token_upper == "USDC":
        if route_pair in usdc_routes:
            return "✓"
    elif token_upper == "USDT":
        # Check both USDT native mesh and USDT0 routes
        if route_pair in usdt_native_routes or route_pair in usdt0_routes:
            return "✓"

    return ""


def render_routes_table_with_selection(df: pd.DataFrame, key: str) -> dict | None:
    """Render routes table with row selection. Returns selected route info."""
    if df.empty:
        st.warning("No routes found for the selected filters.")
        return None

    display_df = df.copy()
    display_df.insert(
        0,
        "Route",
        display_df["Source Token"]
        + " ("
        + display_df["Source Chain"]
        + ") -> "
        + display_df["Dest Token"]
        + " ("
        + display_df["Dest Chain"]
        + ")",
    )

    # Add Zero Fee column - check if tokens match and route exists
    display_df["Zero Fee"] = display_df.apply(
        lambda row: _get_zero_fee_status(
            row["Source Chain"],
            row["Dest Chain"],
            row["Source Token"],
            row["Dest Token"]
        ),
        axis=1,
    )

    # Columns to display (exclude the raw token/chain columns)
    display_columns = ["Route", "Zero Fee", "Volume", "Slippage %", "Transactions"]
    if "Avg Tx Size" in display_df.columns:
        display_columns.append("Avg Tx Size")

    # Use st.dataframe with selection enabled
    event = st.dataframe(
        display_df[display_columns],
        height=ROUTES_TABLE_HEIGHT,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key=key,
        column_config={
            "Route": st.column_config.TextColumn("Route", width="large"),
            "Zero Fee": st.column_config.TextColumn("Zero Fee", width="small", help="✓ indicates a zero-fee bridging path is available"),
            "Volume": st.column_config.NumberColumn("Volume", format="$%.0f"),
            "Slippage %": st.column_config.NumberColumn("Slippage %", format="%.4f%%"),
            "Transactions": st.column_config.NumberColumn("Transactions", format="%d"),
            "Avg Tx Size": st.column_config.NumberColumn("Avg Tx Size", format="$%.0f"),
        },
    )

    # Check if a row is selected
    if event and event.selection and event.selection.rows:
        selected_idx = event.selection.rows[0]
        row = df.iloc[selected_idx]
        route_label = display_df.iloc[selected_idx]["Route"]
        return {
            "route_label": route_label,
            "source_token": row["Source Token"],
            "source_chain": row["Source Chain"],
            "dest_token": row["Dest Token"],
            "dest_chain": row["Dest Chain"],
        }

    return None


def render_route_daily_chart(df: pd.DataFrame, route_label: str) -> None:
    """Render daily volume and transactions chart for a route."""
    if df.empty:
        st.warning("No daily data available for this route.")
        return

    import altair as alt

    # Volume chart
    st.subheader(f"Daily Volume: {route_label}")
    volume_chart = alt.Chart(df).mark_bar(color="#2ecc71").encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Volume:Q", title="Volume ($)"),
        tooltip=[
            alt.Tooltip("Date:T", title="Date"),
            alt.Tooltip("Volume:Q", title="Volume", format="$,.0f"),
        ],
    ).properties(height=250)
    st.altair_chart(volume_chart, use_container_width=True)

    # Transactions chart
    st.subheader(f"Daily Transactions: {route_label}")
    tx_chart = alt.Chart(df).mark_bar(color="#3498db").encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Transactions:Q", title="Transactions"),
        tooltip=[
            alt.Tooltip("Date:T", title="Date"),
            alt.Tooltip("Transactions:Q", title="Transactions", format=","),
        ],
    ).properties(height=250)
    st.altair_chart(tx_chart, use_container_width=True)


def render_daily_chart(df: pd.DataFrame, symbol: str) -> None:
    """Render daily volume and transactions chart."""
    if df.empty:
        st.warning("No daily data available for this token.")
        return

    import altair as alt

    # Volume chart
    st.subheader(f"{symbol} Daily Volume")
    volume_chart = alt.Chart(df).mark_bar(color="#2ecc71").encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Volume:Q", title="Volume ($)"),
        tooltip=[
            alt.Tooltip("Date:T", title="Date"),
            alt.Tooltip("Volume:Q", title="Volume", format="$,.0f"),
        ],
    ).properties(height=250)
    st.altair_chart(volume_chart, use_container_width=True)

    # Transactions chart
    st.subheader(f"{symbol} Daily Transactions")
    tx_chart = alt.Chart(df).mark_bar(color="#3498db").encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Transactions:Q", title="Transactions"),
        tooltip=[
            alt.Tooltip("Date:T", title="Date"),
            alt.Tooltip("Transactions:Q", title="Transactions", format=","),
        ],
    ).properties(height=250)
    st.altair_chart(tx_chart, use_container_width=True)


def render_zero_fee_matrix(
    routes: list[tuple[str, str]],
    token_name: str,
    chain_order: list[str] | None = None,
) -> None:
    """Render a matrix showing zero-fee bridging routes.

    Args:
        routes: List of (source_chain, dest_chain) tuples representing zero-fee routes
        token_name: Name of the token (e.g., "USDC", "USDT")
        chain_order: Optional list specifying the order of chains in the matrix
    """
    if not routes:
        st.warning(f"No zero-fee routes available for {token_name}.")
        return

    # Get unique chains from routes
    route_chains = set()
    for src, dst in routes:
        route_chains.add(src)
        route_chains.add(dst)

    # Use provided chain_order if given, otherwise sort alphabetically
    if chain_order:
        chains = [c for c in chain_order if c in route_chains]
        # Add any chains not in the predefined order
        remaining = sorted([c for c in route_chains if c not in chain_order])
        chains.extend(remaining)
    else:
        chains = sorted(route_chains)

    # Create route set for O(1) lookup
    route_set = set(routes)

    # Build matrix data
    matrix_data = []
    for src in chains:
        row = {"From \\ To": src}
        for dst in chains:
            if src == dst:
                row[dst] = "-"
            elif (src, dst) in route_set:
                row[dst] = "✓"
            else:
                row[dst] = ""
        matrix_data.append(row)

    matrix_df = pd.DataFrame(matrix_data)
    matrix_df = matrix_df.set_index("From \\ To")

    # Custom styling function
    def style_cell(val):
        if val == "✓":
            return "background-color: #2ecc71; color: white; font-weight: bold; text-align: center;"
        elif val == "-":
            return "background-color: #34495e; color: #7f8c8d; text-align: center;"
        else:
            return "background-color: #1a1a2e; text-align: center;"

    styled_df = matrix_df.style.map(style_cell)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            styled_df,
            height=MATRIX_TABLE_HEIGHT,
            use_container_width=True,
        )

    with col2:
        st.markdown("**How to read:**")
        st.markdown("- **Row** = Source Chain")
        st.markdown("- **Column** = Destination Chain")
        st.markdown("- ✓ = Zero-fee bridging available")
        st.markdown("- Empty = Route not available")
        st.markdown(f"- Total routes: **{len(routes)}**")
