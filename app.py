import streamlit as st
from src.database import init_db
from src.const import CACHE_TTL_SHORT, CACHE_TTL_LONG
from src.data_service import (
    get_available_symbols,
    load_slippage_matrix,
    get_transaction_counts,
    get_volume_matrix,
    get_routes_data,
    get_overall_stats,
    get_token_stats,
)
from src.ui.pages import render_per_token_tab, render_routes_tab


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_available_symbols():
    return get_available_symbols()


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_load_slippage_matrix(symbol, days, percentile_type):
    return load_slippage_matrix(symbol, days, percentile_type)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_transaction_counts(symbol, days):
    return get_transaction_counts(symbol, days)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_volume_matrix(symbol, days):
    return get_volume_matrix(symbol, days)


@st.cache_data(ttl=CACHE_TTL_SHORT)
def cached_get_routes_data(days, percentile_type):
    return get_routes_data(days, percentile_type)


@st.cache_data(ttl=CACHE_TTL_LONG)
def cached_get_overall_stats(days):
    return get_overall_stats(days)


@st.cache_data(ttl=CACHE_TTL_LONG)
def cached_get_token_stats(symbol, days):
    return get_token_stats(symbol, days)


def main():
    st.set_page_config(page_title="Stablecoin Bridge Analytics", layout="wide")
    st.title("Stablecoin Bridge Analytics")
    st.markdown("### Cross-Chain Bridging Analysis Dashboard")

    init_db()

    symbols = cached_get_available_symbols()
    if not symbols:
        st.error("No tokens found in database. Please run the collector first.")
        st.stop()

    main_tab1, main_tab2 = st.tabs(["Per Token Analysis", "Routes Analysis"])

    with main_tab1:
        render_per_token_tab(
            symbols=symbols,
            get_token_stats_fn=cached_get_token_stats,
            load_slippage_matrix_fn=cached_load_slippage_matrix,
            get_transaction_counts_fn=cached_get_transaction_counts,
            get_volume_matrix_fn=cached_get_volume_matrix,
        )

    with main_tab2:
        render_routes_tab(
            get_stats_fn=cached_get_overall_stats,
            get_routes_data_fn=cached_get_routes_data,
        )

    st.markdown("---")
    st.caption("**Slippage Formula:** (Amount In - Amount Out) / Amount In x 100%")
    st.caption(
        f"Data is cached for {CACHE_TTL_SHORT // 60} minute(s). "
        "Use Refresh button to force update."
    )


if __name__ == "__main__":
    main()
