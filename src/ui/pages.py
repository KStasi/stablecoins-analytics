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
    render_slippage_matrix,
    render_transaction_counts_matrix,
    render_volume_matrix,
    render_routes_table_with_selection,
    render_routes_stats,
    render_daily_chart,
    render_route_daily_chart,
    get_percentile_label,
    filter_routes_by_stablecoin,
    render_zero_fee_matrix,
)
from src.const import (
    USDC_ZERO_FEE_ROUTES,
    USDT_NATIVE_ZERO_FEE_ROUTES,
    USDT0_ZERO_FEE_ROUTES,
    ZERO_FEE_CHAINS_USDC,
    ZERO_FEE_CHAINS_USDT_NATIVE,
    ZERO_FEE_CHAINS_USDT0,
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
    get_routes_data_fn,
    get_route_daily_stats_fn,
    get_route_slippage_percentile_fn,
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
    col1, col2 = st.columns(2)
    with col1:
        stablecoin_filter = render_stablecoin_filter("stablecoin_filter")
    with col2:
        min_amount, max_amount = render_transaction_size_filter("tx_size_filter")

    st.markdown("---")

    # Get routes data and apply stablecoin filter (always use average slippage)
    routes_df = get_routes_data_fn(start_date, end_date, min_amount, max_amount)
    filtered_routes_df = filter_routes_by_stablecoin(routes_df, stablecoin_filter)

    # Routes-specific stats (based on filtered data)
    render_routes_stats(filtered_routes_df)

    st.markdown("---")

    st.subheader("All Routes - Average Slippage")
    selected_route = render_routes_table_with_selection(filtered_routes_df, "route_selector")

    # Display details for selected route
    if selected_route:
        st.markdown("---")
        st.subheader(f"Route Details: {selected_route['route_label']}")

        # Percentile slider for selected route
        percentile_value = render_percentile_slider("route_percentile")
        percentile_label = get_percentile_label(percentile_value)

        # Calculate and display slippage percentile
        slippage_percentile = get_route_slippage_percentile_fn(
            selected_route["source_token"],
            selected_route["source_chain"],
            selected_route["dest_token"],
            selected_route["dest_chain"],
            percentile_value,
            start_date,
            end_date,
        )

        if slippage_percentile is not None:
            st.metric(f"{percentile_label} Slippage", f"{slippage_percentile:.4f}%")
        else:
            st.metric(f"{percentile_label} Slippage", "N/A")

        st.markdown("---")

        # Daily charts
        daily_stats = get_route_daily_stats_fn(
            selected_route["source_token"],
            selected_route["source_chain"],
            selected_route["dest_token"],
            selected_route["dest_chain"],
            start_date,
            end_date,
        )
        render_route_daily_chart(daily_stats, selected_route["route_label"])


def render_zero_fee_routes_tab() -> None:
    """Render the Zero Fee Routes tab showing USDC and USDT zero-fee bridging matrices."""
    st.header("Zero Fee Bridging Routes")

    st.markdown(
        """
        This page shows all available routes where stablecoins can be bridged with **0% fees**.
        These routes are ideal for cost-effective cross-chain transfers.
        """
    )

    st.markdown("---")

    # USDC Matrix
    st.subheader("USDC Zero-Fee Routes")
    if USDC_ZERO_FEE_ROUTES:
        render_zero_fee_matrix(USDC_ZERO_FEE_ROUTES, "USDC", ZERO_FEE_CHAINS_USDC)
    else:
        st.info("No USDC zero-fee routes configured yet.")

    st.markdown("---")

    # USDT Native Mesh Matrix
    st.subheader("USDT Native Mesh Zero-Fee Routes")
    st.caption("USDT Native Mesh - Native USDT on various chains")
    if USDT_NATIVE_ZERO_FEE_ROUTES:
        render_zero_fee_matrix(USDT_NATIVE_ZERO_FEE_ROUTES, "USDT Native Mesh", ZERO_FEE_CHAINS_USDT_NATIVE)
    else:
        st.info("No USDT Native Mesh zero-fee routes configured yet.")

    st.markdown("---")

    # USDT0 Matrix
    st.subheader("USDT0 Zero-Fee Routes")
    st.caption("USDT0 - Bridged/wrapped USDT via LayerZero OFT standard")
    if USDT0_ZERO_FEE_ROUTES:
        render_zero_fee_matrix(USDT0_ZERO_FEE_ROUTES, "USDT0", ZERO_FEE_CHAINS_USDT0)
    else:
        st.info("No USDT0 zero-fee routes configured yet.")
