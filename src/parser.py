from src.database import Token
from src.const import (
    CHAIN_ID_MAP,
    TOKEN_LOOKUP,
    UNKNOWN_SYMBOL,
)


def normalize_address(address: str | None) -> str:
    """Normalize address, converting native token markers to 'native'."""
    if not address or address == "11111111111111111111":
        return "native"
    return address


def lookup_symbol(chain: str | None, address: str | None) -> str:
    """Look up symbol from chain and address using TOKEN_LOOKUP."""
    if not chain:
        return UNKNOWN_SYMBOL

    chain_upper = chain.upper()
    address_lower = normalize_address(address).lower()

    return TOKEN_LOOKUP.get((chain_upper, address_lower), UNKNOWN_SYMBOL)


def parse_nep141_asset(asset_id: str) -> dict:
    """
    Parse nep141 asset IDs.

    Formats:
    - OMFT: nep141:chain-address.omft.near or nep141:chain.omft.near
    - Native NEAR: nep141:token.near or nep141:token.subdomain.near
    """
    content = asset_id[7:]  # Remove "nep141:"

    if content.endswith(".omft.near"):
        # OMFT token
        content = content[:-10]  # Remove ".omft.near"
        if "-" in content:
            chain, address = content.split("-", 1)
        else:
            chain = content
            address = "native"
    else:
        # Native NEAR token (e.g., wrap.near, token.sweat, usdt.tether-token.near)
        chain = "NEAR"
        address = content

    symbol = lookup_symbol(chain, address)
    return {"chain": chain, "address": address, "symbol": symbol}


def parse_nep245_asset(asset_id: str) -> dict:
    """
    Parse nep245 (Omni protocol) asset IDs.

    Format: nep245:v2_1.omni.hot.tg:{chain_id}_{address}
    Example: nep245:v2_1.omni.hot.tg:56_11111111111111111111
    """
    # Find the last colon which separates the chain_id_address part
    last_colon = asset_id.rfind(":")
    if last_colon == -1:
        return {"chain": None, "address": None, "symbol": UNKNOWN_SYMBOL}

    chain_id_address = asset_id[last_colon + 1:]

    if "_" not in chain_id_address:
        return {"chain": None, "address": None, "symbol": UNKNOWN_SYMBOL}

    chain_id, address = chain_id_address.split("_", 1)
    chain = CHAIN_ID_MAP.get(chain_id)

    if not chain:
        return {"chain": None, "address": address, "symbol": UNKNOWN_SYMBOL}

    address = normalize_address(address)
    symbol = lookup_symbol(chain, address)
    return {"chain": chain, "address": address, "symbol": symbol}


def parse_1cs_v1_asset(asset_id: str) -> dict:
    """
    Parse 1cs_v1 (cross-chain swap) asset IDs.

    Format: 1cs_v1:{chain}:{token_type}:{address}
    Examples:
    - 1cs_v1:sol:spl:A7bdiYdS5GjqGFtxf17ppRHtDKPkkRqbKtR27dxvQXaS
    - 1cs_v1:base:erc20:0x0382e3fee4a420bd446367d468a6f00225853420
    - 1cs_v1:near:nep141:zec.omft.near
    """
    parts = asset_id.split(":")
    if len(parts) < 4:
        return {"chain": None, "address": None, "symbol": UNKNOWN_SYMBOL}

    chain = parts[1].upper()
    # token_type = parts[2]  # spl, erc20, nep141 etc. (not used for lookup)
    address = ":".join(parts[3:])  # Rejoin in case address contains colons

    symbol = lookup_symbol(chain, address)
    return {"chain": chain, "address": address, "symbol": symbol}


def parse_asset_id(asset_id: str) -> dict:
    """
    Parse asset ID and return chain, address, and symbol.

    Supports multiple protocols:
    - nep141: NEAR tokens (OMFT and native)
    - nep245: Omni protocol tokens
    - 1cs_v1: Cross-chain swap tokens
    """
    if not asset_id:
        return {"chain": None, "address": None, "symbol": None}

    if asset_id.startswith("nep245:"):
        return parse_nep245_asset(asset_id)
    elif asset_id.startswith("1cs_v1:"):
        return parse_1cs_v1_asset(asset_id)
    elif asset_id.startswith("nep141:"):
        return parse_nep141_asset(asset_id)
    else:
        # Unknown protocol
        return {"chain": None, "address": None, "symbol": UNKNOWN_SYMBOL}


def get_or_create_token(db, asset_id: str) -> Token:
    """Get existing token or create new one."""
    token = db.query(Token).filter_by(asset_id=asset_id).first()

    if not token:
        parsed = parse_asset_id(asset_id)
        token = Token(
            symbol=parsed["symbol"] or UNKNOWN_SYMBOL,
            asset_id=asset_id,
            chain=parsed["chain"],
            address=parsed["address"],
        )
        db.add(token)
        db.flush()

    return token
