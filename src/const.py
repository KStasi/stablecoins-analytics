# =============================================================================
# CHAIN ID MAPPING (for nep245 Omni protocol)
# =============================================================================
CHAIN_ID_MAP = {
    "1": "ETH",
    "10": "OP",
    "56": "BNB",
    "137": "POLYGON",
    "143": "BERACHAIN",
    "196": "XLAYER",
    "1100": "VELAS",
    "1117": "XDAI",
    "9745": "RARI",
    "43114": "AVAX",
}

# =============================================================================
# TOKEN MAPPINGS (chain, address) -> symbol
# =============================================================================
TOKEN_MAPPINGS = [
    {"chain": "BNB", "symbol": "BNB", "address": "native"},
    {"chain": "SOL", "symbol": "SOL", "address": "native"},
    {"chain": "BASE", "symbol": "ETH", "address": "native"},
    {"chain": "ARB", "symbol": "ETH", "address": "native"},
    {"chain": "NEAR", "symbol": "NEAR", "address": "17208628f84f5d6ad33f0da3bbbeb27ffcb398eac501a31bd6ad2011e36133a1"},
    {"chain": "NEAR", "symbol": "WNEAR", "address": "wrap.near"},
    {"chain": "POLYGON", "symbol": "USDC", "address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
    {"chain": "BNB", "symbol": "USDT", "address": "0x55d398326f99059ff775485246999027b3197955"},
    {"chain": "ETH", "symbol": "AURORA", "address": "0xaaaaaa20d9e0e2461697782ef11675f668207961"},
    {"chain": "BTC", "symbol": "BTC", "address": "native"},
    {"chain": "SOL", "symbol": "cbBTC", "address": "c800a4bd850783ccb82c2b2c7e84175443606352"},
    {"chain": "ETH", "symbol": "USDT", "address": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
    {"chain": "XRP", "symbol": "XRP", "address": "native"},
    {"chain": "ETH", "symbol": "ETH", "address": "native"},
    {"chain": "SOL", "symbol": "HYPE", "address": "5ce3bf3a31af18be40ba30f721101b4341690186"},
    {"chain": "ARB", "symbol": "USDC", "address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831"},
    {"chain": "XDAI", "symbol": "XDAI", "address": "native"},
    {"chain": "NEAR", "symbol": "SWEAT", "address": "token.sweat"},
    {"chain": "TRON", "symbol": "TRX", "address": "native"},
    {"chain": "TRON", "symbol": "USDT", "address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
    {"chain": "POLYGON", "symbol": "USDT", "address": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"},
    {"chain": "BASE", "symbol": "USDC", "address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"},
    {"chain": "NEAR", "symbol": "USDt", "address": "usdt.tether-token.near"},
    {"chain": "AVAX", "symbol": "AVAX", "address": "native"},
    {"chain": "AVAX", "symbol": "USDC", "address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e"},
    {"chain": "BCH", "symbol": "BCH", "address": "native"},
    {"chain": "ETH", "symbol": "USDC", "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
    {"chain": "BNB", "symbol": "USDC", "address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"},
    {"chain": "XDAI", "symbol": "GNO", "address": "0x9c58bacc331c9aa871afd802db6379a98e80cedb"},
    {"chain": "GNOSIS", "symbol": "USDC", "address": "0x4ecaba5870353805a9f068101a40e0f32ed605c6"},
    {"chain": "ZEC", "symbol": "ZEC", "address": "native"},
    {"chain": "AVAX", "symbol": "USDT", "address": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7"},
    {"chain": "POLYGON", "symbol": "MATIC", "address": "native"},
    {"chain": "OP", "symbol": "USDC", "address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"},
    {"chain": "LTC", "symbol": "LTC", "address": "native"},
    {"chain": "OP", "symbol": "USDT", "address": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58"},
    {"chain": "VELAS", "symbol": "VLX", "address": "native"},
    {"chain": "ETH", "symbol": "DAI", "address": "0x6b175474e89094c44da98b954eedeac495271d0f"},
    {"chain": "ETH", "symbol": "SHIB", "address": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"},
    {"chain": "NEAR", "symbol": "ETH", "address": "eth.bridge.near"},
    {"chain": "GNOSIS", "symbol": "USDT", "address": "0x2a22f9c3b484c3629090feed35f17ff8f88f76f0"},
    {"chain": "BERA", "symbol": "BERA", "address": "native"},
    {"chain": "OP", "symbol": "ETH", "address": "native"},
    {"chain": "BASE", "symbol": "cbBTC", "address": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf"},
    {"chain": "BASE", "symbol": "USDz", "address": "0x227d920e20ebac8a40e7d6431b7d724bb64d7245"},
    {"chain": "BERACHAIN", "symbol": "BERA", "address": "native"},
    {"chain": "ARB", "symbol": "ARB", "address": "0x912ce59144191c1204e64559fe8253a0e49e6548"},
    {"chain": "ARB", "symbol": "USDT", "address": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9"},
    {"chain": "DOGE", "symbol": "DOGE", "address": "native"},
    {"chain": "BNB", "symbol": "BTCB", "address": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c"},
    {"chain": "BNB", "symbol": "CAKE", "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"},
    {"chain": "BERACHAIN", "symbol": "HONEY", "address": "0x0e4aaf1351de4c0264c5c7056ef3777b41bd8e03"},
    {"chain": "GNOSIS", "symbol": "xDAI", "address": "native"},
    {"chain": "SOL", "symbol": "RAY", "address": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"},
    {"chain": "APTOS", "symbol": "zUSDC", "address": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"},
    {"chain": "BNB", "symbol": "ETH", "address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8"},
    {"chain": "ETH", "symbol": "NEIRO", "address": "0xdef1b2d939edc0e4d35806c59b3166f790175afe"},
    {"chain": "NEAR", "symbol": "PAI", "address": "token.publicailab.near"},
    {"chain": "ETH", "symbol": "cbBTC", "address": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf"},
    {"chain": "NEAR", "symbol": "NPRO", "address": "npro.nearmobile.near"},
    {"chain": "SOL", "symbol": "RENDER", "address": "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof"},
    {"chain": "NEAR", "symbol": "RHEA", "address": "token.rhealab.near"},
    {"chain": "BERACHAIN", "symbol": "YEET", "address": "0x1740f679325ef3686b2f574e392007a92e4bed41"},
    {"chain": "ETH", "symbol": "WBTC", "address": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"},
    {"chain": "SUI", "symbol": "SUI", "address": "native"},
    {"chain": "GNOSIS", "symbol": "WETH", "address": "0x6a023ccd1ff6f2045c3309768ead9e68f978f6e1"},
    {"chain": "VELAS", "symbol": "USDV", "address": "0x01445c31581c354b7338ac35693ab2001b50b9ae"},
    {"chain": "RARI", "symbol": "ETH", "address": "native"},
    {"chain": "GNOSIS", "symbol": "GNO", "address": "0x9c58bacc331c9aa871afd802db6379a98e80cedb"},
    {"chain": "NEAR", "symbol": "BLACKDRAGON", "address": "blackdragon.tkn.near"},
    {"chain": "RARI", "symbol": "USDC", "address": "0xa219439258ca9da29e9cc4ce5596924745e12b93"},
    {"chain": "GNOSIS", "symbol": "COW", "address": "0x177127622c4a00f3d409b75571e12cb3c8973d3c"},
    {"chain": "SOL", "symbol": "PYTH", "address": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3"},
    {"chain": "ETH", "symbol": "SWARMS", "address": "0xb4b9dc1c77bdbb135ea907fd5a08094d98883a35"},
    {"chain": "SUI", "symbol": "USDC", "address": "0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN"},
    {"chain": "ETH", "symbol": "PEPE", "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933"},
    {"chain": "NEAR", "symbol": "nBTC", "address": "nbtc.bridge.near"},
    {"chain": "NEAR", "symbol": "SHITZU", "address": "token.0xshitzu.near"},
    {"chain": "BNB", "symbol": "FDUSD", "address": "0xc5f0f7b66764f6ec8c8dff7ba683102295e16409"},
    {"chain": "NEAR", "symbol": "MPDA", "address": "mpdao-token.near"},
    {"chain": "ARB", "symbol": "PEAS", "address": "0xca7dec8550f43a5e46e3dfb95801f64280e75b27"},
    {"chain": "BERA", "symbol": "HONEY", "address": "0x779ded0c9e1022225f8e0630b35a9b54be713736"},
    {"chain": "CARDANO", "symbol": "ADA", "address": "native"},
    {"chain": "GNOSIS", "symbol": "WXDAI", "address": "0x5cb9073902f2035222b9749f8fb0c9bfe5527108"},
    {"chain": "BASE", "symbol": "BASED", "address": "0x0382e3fee4a420bd446367d468a6f00225853420"},
    {"chain": "GNOSIS", "symbol": "sDAI", "address": "0x420ca0f9b9b604ce0fd9c18ef134c705e5fa3430"},
    {"chain": "APTOS", "symbol": "APT", "address": "native"},
    {"chain": "ETH", "symbol": "SMR", "address": "0x8b1484d57abbe239bb280661377363b03c89caea"},
    {"chain": "BASE", "symbol": "VIRTUAL", "address": "0x98d0baa52b2d063e780de12f615f963fe8537553"},
    {"chain": "STARKNET", "symbol": "STRK", "address": "native"},
    {"chain": "XLAYER", "symbol": "USDT", "address": "0x1e4a5963abfd975d8c9021ce480b42188849d41d"},
    {"chain": "NEAR", "symbol": "ITLX", "address": "itlx.intellex_xyz.near"},
    {"chain": "ETH", "symbol": "SPX", "address": "0xe0f63a424a4439cbe457d80e4f4b51ad25b2c56c"},
    {"chain": "NEAR", "symbol": "JAMBO", "address": "jambo-1679.meme-cooking.near"},
    {"chain": "XLAYER", "symbol": "ETH", "address": "native"},
    {"chain": "NEAR", "symbol": "CFI", "address": "cfi.consumer-fi.near"},
    {"chain": "SOL", "symbol": "JTO", "address": "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL"},
    # Bridge tokens on NEAR (with .factory.bridge.near suffix)
    {"chain": "NEAR", "symbol": "AURORA", "address": "aaaaaa20d9e0e2461697782ef11675f668207961.factory.bridge.near"},
    # TRON USDT uses different address format in OMFT
    {"chain": "TRON", "symbol": "USDT", "address": "d28a265909efecdcee7c5028585214ea0b96f015"},
]


def _build_token_lookup() -> dict:
    """Build lookup index: (chain_upper, address_lower) -> symbol"""
    lookup = {}
    for mapping in TOKEN_MAPPINGS:
        chain = mapping["chain"].upper()
        address = mapping["address"].lower()
        symbol = mapping["symbol"]
        lookup[(chain, address)] = symbol
    return lookup


TOKEN_LOOKUP = _build_token_lookup()

# =============================================================================
# SUPPORTED CHAINS (for UI display)
# Must match chain names in TOKEN_MAPPINGS (lowercase)
# =============================================================================
CHAINS = ["eth", "arb", "base", "op", "polygon", "bnb", "avax", "sol"]

# =============================================================================
# DEFAULT VALUES
# =============================================================================
UNKNOWN_SYMBOL = "UNKNOWN"
NA_PLACEHOLDER = "N/A"
SAME_CHAIN_SLIPPAGE = 0.0

# =============================================================================
# STABLECOINS (case-insensitive matching)
# =============================================================================
STABLECOINS = {
    "USDT", "USDC", "DAI", "USDD", "TUSD", "BUSD", "FRAX", "USDP", "GUSD",
    "USDS", "USDM", "USDJ", "USDN", "USDX", "USDK", "USDZ", "USDSM",
    "FDUSD", "PYUSD", "EURC", "EURT", "EURS", "SDAI", "CUSD", "CEUR",
}

# =============================================================================
# TRANSACTION SIZE FILTERS (label -> (min, max) or None for no limit)
# =============================================================================
TRANSACTION_SIZE_FILTERS = {
    "All Sizes": (None, None),
    "Under $1,000": (None, 1000),
    "$1,000 - $10,000": (1000, 10000),
    "$10,000 - $100,000": (10000, 100000),
    "$100,000+": (100000, None),
}

# =============================================================================
# API SETTINGS
# =============================================================================
API_URL = "https://explorer.near-intents.org/api/v0/transactions"

# =============================================================================
# DATA COLLECTION SETTINGS
# =============================================================================
DATA_START_DATE = "2025-10-01"
PAGINATION_SIZE = 1000
API_RATE_LIMIT_DELAY = 5.1

# =============================================================================
# SCHEDULER SETTINGS
# =============================================================================
COLLECTION_INTERVAL_HOURS = 6
SCHEDULER_SLEEP_SECONDS = 60

# =============================================================================
# CACHE TTL (seconds)
# =============================================================================
CACHE_TTL_SHORT = 60
CACHE_TTL_LONG = 300

# =============================================================================
# UI DISPLAY SETTINGS
# =============================================================================
ASSET_ID_DISPLAY_LONG = 70
ASSET_ID_DISPLAY_SHORT = 50
MATRIX_TABLE_HEIGHT = 300
ROUTES_TABLE_HEIGHT = 600
DECIMAL_PLACES = 4

# =============================================================================
# DEFAULT UI INDICES
# =============================================================================
DEFAULT_TIME_PERIOD_INDEX = 3  # "All Time"
DEFAULT_PERCENTILE_INDEX = 0  # "Average"

# =============================================================================
# TIME PERIODS (label -> days, None for all time)
# =============================================================================
TIME_PERIODS = {
    "1 Day": 1,
    "7 Days": 7,
    "30 Days": 30,
    "All Time": None,
}

# =============================================================================
# PERCENTILE OPTIONS (label -> percentile value or "avg")
# =============================================================================
PERCENTILE_OPTIONS = {
    "Average": "avg",
    "Median (P50)": 50,
    "P25": 25,
    "P75": 75,
    "P95": 95,
    "P99": 99,
}

# =============================================================================
# API RESPONSE FIELD NAMES
# =============================================================================
FIELD_DEPOSIT_KEY = "depositAddressAndMemo"
FIELD_ORIGIN_ASSET = "originAsset"
FIELD_DEST_ASSET = "destinationAsset"
FIELD_AMOUNT_IN = "amountInUsd"
FIELD_AMOUNT_OUT = "amountOutUsd"
FIELD_CREATED_AT = "createdAt"
FIELD_DEPOSIT_ADDRESS = "depositAddress"
FIELD_STATUS = "status"
FIELD_INTENT_HASHES = "intentHashes"
FIELD_DATA = "data"
