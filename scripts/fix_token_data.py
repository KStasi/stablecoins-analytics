"""
Script to fix token data in the database by re-parsing asset IDs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, Token, init_db
from src.parser import parse_asset_id


def fix_token_data(dry_run: bool = False) -> None:
    """Re-parse all tokens and update chain, address, and symbol fields."""
    init_db()
    db = SessionLocal()

    try:
        tokens = db.query(Token).all()

        updated_count = 0
        unchanged_count = 0

        for token in tokens:
            parsed = parse_asset_id(token.asset_id)

            new_chain = parsed["chain"]
            new_address = parsed["address"]
            new_symbol = parsed["symbol"]

            changes = []
            if token.chain != new_chain:
                changes.append(f"chain: {token.chain} -> {new_chain}")
            if token.address != new_address:
                changes.append(f"address: {token.address} -> {new_address}")
            if token.symbol != new_symbol:
                changes.append(f"symbol: {token.symbol} -> {new_symbol}")

            if changes:
                print(
                    f"{'[DRY RUN] ' if dry_run else ''}"
                    f"Token {token.id} ({token.asset_id[:60]}...):"
                )
                for change in changes:
                    print(f"    {change}")

                if not dry_run:
                    token.chain = new_chain
                    token.address = new_address
                    token.symbol = new_symbol

                updated_count += 1
            else:
                unchanged_count += 1

        if not dry_run:
            db.commit()

        print(f"\n{'=' * 60}")
        print(f"{'[DRY RUN] ' if dry_run else ''}Summary:")
        print(f"  Updated: {updated_count}")
        print(f"  Unchanged: {unchanged_count}")
        print(f"  Total tokens: {len(tokens)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix token data in database")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    args = parser.parse_args()

    fix_token_data(dry_run=args.dry_run)
