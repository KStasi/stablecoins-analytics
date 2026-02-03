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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Routes", 0)
        with col2:
            st.metric("Average Slippage", "N/A")
        with col3:
            st.metric("Total Volume", "$0")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Routes", len(df))

    with col2:
        avg_slippage = df["Slippage %"].mean()
        st.metric("Average Slippage", f"{avg_slippage:.{DECIMAL_PLACES}f}%")

    with col3:
        total_volume = df["Volume"].sum()
        st.metric("Total Volume", f"${total_volume:,.0f}")


def render_routes_table(df: pd.DataFrame, percentile_label: str) -> None:
    """Render routes table with formatting."""
    if df.empty:
        st.warning("No routes found for the selected filters.")
        return

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

    # Build format dict based on available columns
    format_dict = {
        "Volume": "${:,.0f}",
        "Slippage %": f"{{:.{DECIMAL_PLACES}f}}%",
        "Transactions": "{:,}",
    }

    if "Median Tx Size" in display_df.columns:
        format_dict["Median Tx Size"] = "${:,.0f}"

    st.dataframe(
        display_df.style.format(format_dict)
        .background_gradient(
            subset=["Slippage %"],
            cmap="RdYlGn_r",
            vmin=0,
            vmax=display_df["Slippage %"].max() if not display_df.empty else 1,
        )
        .background_gradient(subset=["Volume"], cmap="Greens"),
        height=ROUTES_TABLE_HEIGHT,
        use_container_width=True,
    )


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
