import streamlit as st
from src.const import TIME_PERIODS, PERCENTILE_OPTIONS
from src.ui.components import (
    render_symbol_selector,
    render_time_period_selector,
    render_percentile_selector,
    render_refresh_button,
    render_token_stats_row,
    render_stats_row,
    render_slippage_matrix,
    render_transaction_counts_matrix,
    render_volume_matrix,
    render_routes_table,
)


def render_per_token_tab(
    symbols: list[str],
    get_token_stats_fn,
    load_slippage_matrix_fn,
    get_transaction_counts_fn,
    get_volume_matrix_fn,
) -> None:
    """Render the Per Token Analysis tab."""
    st.header("Per Token Analysis")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        selected_symbol = render_symbol_selector(symbols, "symbol_tab1")

    with col2:
        days_filter = render_time_period_selector("period_tab1")
        selected_period = list(TIME_PERIODS.keys())[
            list(TIME_PERIODS.values()).index(days_filter)
        ]

    with col3:
        percentile_value = render_percentile_selector("percentile_tab1")
        selected_percentile_label = list(PERCENTILE_OPTIONS.keys())[
            list(PERCENTILE_OPTIONS.values()).index(percentile_value)
        ]

    with col4:
        if render_refresh_button("refresh_tab1"):
            st.cache_data.clear()
            st.rerun()

    token_stats = get_token_stats_fn(selected_symbol, days_filter)
    render_token_stats_row(token_stats, selected_period)

    st.markdown("---")

    st.subheader(f"Slippage Matrix (%) - {selected_percentile_label}")
    slippage_matrix = load_slippage_matrix_fn(
        selected_symbol, days_filter, percentile_value
    )
    render_slippage_matrix(slippage_matrix, selected_percentile_label)

    st.markdown("---")

    sub_tab1, sub_tab2 = st.tabs(["Transaction Counts", "Volume"])

    with sub_tab1:
        tx_counts = get_transaction_counts_fn(selected_symbol, days_filter)
        render_transaction_counts_matrix(tx_counts)

    with sub_tab2:
        volume_matrix = get_volume_matrix_fn(selected_symbol, days_filter)
        render_volume_matrix(volume_matrix)


def render_routes_tab(
    get_stats_fn,
    get_routes_data_fn,
) -> None:
    """Render the Routes Analysis tab."""
    st.header("Routes Analysis")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        days_filter = render_time_period_selector("period_tab2")
        selected_period = list(TIME_PERIODS.keys())[
            list(TIME_PERIODS.values()).index(days_filter)
        ]

    with col2:
        percentile_value = render_percentile_selector("percentile_tab2")
        selected_percentile_label = list(PERCENTILE_OPTIONS.keys())[
            list(PERCENTILE_OPTIONS.values()).index(percentile_value)
        ]

    with col3:
        if render_refresh_button("refresh_tab2"):
            st.cache_data.clear()
            st.rerun()

    overall_stats = get_stats_fn(days_filter)
    render_stats_row(overall_stats, selected_period)

    st.markdown("---")

    st.subheader(f"All Routes - {selected_percentile_label} Slippage")
    routes_df = get_routes_data_fn(days_filter, percentile_value)
    render_routes_table(routes_df, selected_percentile_label)
