import streamlit as st
from src.database import init_db
from src.const import CACHE_TTL_SHORT, CACHE_TTL_LONG
from src.data_service import (
    get_available_symbols,
    get_earliest_transaction_date,
    load_slippage_matrix,
    get_transaction_counts,
    get_volume_matrix,
    get_routes_data,
    get_route_daily_stats,
    get_route_slippage_percentile,
    get_token_stats,
    get_token_daily_stats,
)
from src.ui.pages import render_same_token_tab, render_routes_tab, render_zero_fee_routes_tab
from src.auth import require_auth


@st.cache_data(ttl=CACHE_TTL_LONG)
def cached_get_earliest_date():
    return get_earliest_transaction_date()


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_available_symbols():
    return get_available_symbols()


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_load_slippage_matrix(symbol, start_date, end_date, percentile_type):
    return load_slippage_matrix(symbol, start_date, end_date, percentile_type)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_transaction_counts(symbol, start_date, end_date):
    return get_transaction_counts(symbol, start_date, end_date)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_volume_matrix(symbol, start_date, end_date):
    return get_volume_matrix(symbol, start_date, end_date)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_routes_data(start_date, end_date, min_amount, max_amount):
    return get_routes_data(start_date, end_date, min_amount, max_amount)


@st.cache_data(ttl=CACHE_TTL_LONG)
def cached_get_token_stats(symbol, start_date, end_date):
    return get_token_stats(symbol, start_date, end_date)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_token_daily_stats(symbol, start_date, end_date):
    return get_token_daily_stats(symbol, start_date, end_date)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_route_daily_stats(source_token, source_chain, dest_token, dest_chain, start_date, end_date):
    return get_route_daily_stats(source_token, source_chain, dest_token, dest_chain, start_date, end_date)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_route_slippage_percentile(source_token, source_chain, dest_token, dest_chain, percentile_type, start_date, end_date):
    return get_route_slippage_percentile(source_token, source_chain, dest_token, dest_chain, percentile_type, start_date, end_date)


def main():
    st.set_page_config(page_title="Stablecoin Bridge Analytics", layout="wide")

    # Require authentication before showing any content
    require_auth()

    init_db()

    symbols = cached_get_available_symbols()
    if not symbols:
        st.error("No tokens found in database. Please run the collector first.")
        st.stop()

    earliest_date = cached_get_earliest_date()

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Routes Analysis", "Same Token Transfers", "Zero Fee Routes"],
            label_visibility="collapsed",
        )

    st.title("Stablecoin Bridge Analytics")
    st.markdown("### Cross-Chain Bridging Analysis Dashboard")

    if page == "Routes Analysis":
        render_routes_tab(
            earliest_date=earliest_date,
            get_routes_data_fn=cached_get_routes_data,
            get_route_daily_stats_fn=cached_get_route_daily_stats,
            get_route_slippage_percentile_fn=cached_get_route_slippage_percentile,
        )
    elif page == "Same Token Transfers":
        render_same_token_tab(
            symbols=symbols,
            earliest_date=earliest_date,
            get_token_stats_fn=cached_get_token_stats,
            load_slippage_matrix_fn=cached_load_slippage_matrix,
            get_transaction_counts_fn=cached_get_transaction_counts,
            get_volume_matrix_fn=cached_get_volume_matrix,
            get_token_daily_stats_fn=cached_get_token_daily_stats,
        )
    else:  # Zero Fee Routes
        render_zero_fee_routes_tab()

    st.markdown("---")
    st.caption("**Slippage Formula:** (Amount In - Amount Out) / Amount In x 100%")


if __name__ == "__main__":
    main()
