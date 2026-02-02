import streamlit as st
import pandas as pd
from src.const import (
    TIME_PERIODS,
    PERCENTILE_OPTIONS,
    DEFAULT_TIME_PERIOD_INDEX,
    DEFAULT_PERCENTILE_INDEX,
    MATRIX_TABLE_HEIGHT,
    ROUTES_TABLE_HEIGHT,
    DECIMAL_PLACES,
    NA_PLACEHOLDER,
)


def render_symbol_selector(symbols: list[str], key: str) -> str:
    """Render symbol selector and return selected symbol."""
    return st.selectbox("Select Token:", symbols, key=key)


def render_time_period_selector(key: str) -> int | None:
    """Render time period selector and return days filter."""
    selected_period = st.selectbox(
        "Time Period:",
        list(TIME_PERIODS.keys()),
        index=DEFAULT_TIME_PERIOD_INDEX,
        key=key,
    )
    return TIME_PERIODS[selected_period]


def render_percentile_selector(key: str) -> str | int:
    """Render percentile selector and return percentile value."""
    selected_label = st.selectbox(
        "Slippage Metric:",
        list(PERCENTILE_OPTIONS.keys()),
        index=DEFAULT_PERCENTILE_INDEX,
        key=key,
    )
    return PERCENTILE_OPTIONS[selected_label]


def render_refresh_button(key: str) -> bool:
    """Render refresh button and return if clicked."""
    return st.button("Refresh", use_container_width=True, key=key)


def render_stats_row(stats: dict, period_label: str) -> None:
    """Render a row of statistics metrics."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transactions", f"{stats['transactions']:,}")
    with col2:
        st.metric("Total Volume", f"${stats['volume']:,.0f}")
    with col3:
        st.metric("Period", period_label)


def render_token_stats_row(stats: dict, period_label: str) -> None:
    """Render a row of token-specific statistics."""
    symbol = stats.get("symbol", NA_PLACEHOLDER)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{symbol} Transactions", f"{stats['transactions']:,}")
    with col2:
        st.metric(f"{symbol} Volume", f"${stats['volume']:,.0f}")
    with col3:
        st.metric("Period", period_label)


def render_slippage_matrix(matrix: pd.DataFrame, percentile_label: str) -> None:
    """Render slippage matrix with formatting."""
    if matrix.empty:
        st.warning("No data available for this token.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            matrix.style.format(
                f"{{:.{DECIMAL_PLACES}f}}", na_rep=NA_PLACEHOLDER
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


def render_routes_table(df: pd.DataFrame, percentile_label: str) -> None:
    """Render routes table with formatting."""
    if df.empty:
        st.warning("No routes found for the selected period.")
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

    st.dataframe(
        display_df.style.format({
            "Volume": "${:,.0f}",
            "Slippage %": f"{{:.{DECIMAL_PLACES}f}}",
            "Transactions": "{:,}",
        })
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

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Routes", len(df))

    with col2:
        avg_slippage = df["Slippage %"].mean()
        st.metric("Average Slippage", f"{avg_slippage:.{DECIMAL_PLACES}f}%")

    with col3:
        total_volume = df["Volume"].sum()
        st.metric("Total Volume", f"${total_volume:,.0f}")
