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
)


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

    # Columns to display (exclude the raw token/chain columns)
    display_columns = ["Route", "Volume", "Slippage %", "Transactions"]
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
