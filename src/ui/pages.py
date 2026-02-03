import streamlit as st
from datetime import date
from src.ui.components import (
    render_symbol_selector,
    render_date_range_selector,
    render_percentile_slider,
    render_stablecoin_filter,
    render_transaction_size_filter,
    render_refresh_button,
    render_token_stats_row,
    render_stats_row,
    render_slippage_matrix,
    render_transaction_counts_matrix,
    render_volume_matrix,
    render_routes_table,
    render_routes_stats,
    render_daily_chart,
    get_percentile_label,
    filter_routes_by_stablecoin,
)


def render_same_token_tab(
    symbols: list[str],
    earliest_date: date | None,
    get_token_stats_fn,
    load_slippage_matrix_fn,
    get_transaction_counts_fn,
    get_volume_matrix_fn,
    get_token_daily_stats_fn,
) -> None:
    """Render the Same Token Transfers tab."""
    st.header("Same Token Cross-Chain Transfers")

    # Row 1: Token selector and Refresh button
    col1, col2 = st.columns([3, 1])

    with col1:
        selected_symbol = render_symbol_selector(symbols, "symbol_tab1")

    with col2:
        if render_refresh_button("refresh_tab1"):
            st.cache_data.clear()
            st.rerun()

    # Row 2: Date range selector
    st.subheader("Time Period")
    start_date, end_date = render_date_range_selector("period_tab1", earliest_date)

    # Row 3: Percentile slider
    percentile_value = render_percentile_slider("percentile_tab1")
    percentile_label = get_percentile_label(percentile_value)

    st.markdown("---")

    token_stats = get_token_stats_fn(selected_symbol, start_date, end_date)
    render_token_stats_row(token_stats)

    st.markdown("---")

    # Daily chart
    daily_stats = get_token_daily_stats_fn(selected_symbol, start_date, end_date)
    render_daily_chart(daily_stats, selected_symbol)

    st.markdown("---")

    st.subheader(f"Slippage Matrix - {percentile_label}")
    slippage_matrix = load_slippage_matrix_fn(
        selected_symbol, start_date, end_date, percentile_value
    )
    render_slippage_matrix(slippage_matrix, percentile_label)

    st.markdown("---")

    sub_tab1, sub_tab2 = st.tabs(["Transaction Counts", "Volume"])

    with sub_tab1:
        tx_counts = get_transaction_counts_fn(selected_symbol, start_date, end_date)
        render_transaction_counts_matrix(tx_counts)

    with sub_tab2:
        volume_matrix = get_volume_matrix_fn(selected_symbol, start_date, end_date)
        render_volume_matrix(volume_matrix)


def render_routes_tab(
    earliest_date: date | None,
    get_stats_fn,
    get_routes_data_fn,
) -> None:
    """Render the Routes Analysis tab."""
    st.header("Routes Analysis")

    # Row 1: Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if render_refresh_button("refresh_tab2"):
            st.cache_data.clear()
            st.rerun()

    # Row 2: Date range selector
    st.subheader("Time Period")
    start_date, end_date = render_date_range_selector("period_tab2", earliest_date)

    # Row 3: Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        percentile_value = render_percentile_slider("percentile_tab2")
        percentile_label = get_percentile_label(percentile_value)
    with col2:
        stablecoin_filter = render_stablecoin_filter("stablecoin_filter")
    with col3:
        min_amount, max_amount = render_transaction_size_filter("tx_size_filter")

    st.markdown("---")

    # Get routes data and apply stablecoin filter
    routes_df = get_routes_data_fn(start_date, end_date, percentile_value, min_amount, max_amount)
    filtered_routes_df = filter_routes_by_stablecoin(routes_df, stablecoin_filter)

    # Stats row (after filters, before table)
    overall_stats = get_stats_fn(start_date, end_date)
    render_stats_row(overall_stats)

    # Routes-specific stats
    render_routes_stats(filtered_routes_df)

    st.markdown("---")

    st.subheader(f"All Routes - {percentile_label} Slippage")
    render_routes_table(filtered_routes_df, percentile_label)
