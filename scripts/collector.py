import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db
from src.api_client import fetch_transactions_page
from src.transaction_service import store_transactions
from src.cache_service import update_slippage_cache
from src.const import (
    PAGINATION_SIZE,
    MAX_PAGES_DEFAULT,
    API_RATE_LIMIT_DELAY,
    DATA_START_DATE,
    FIELD_DATA,
)


def collect_data(max_pages: int = MAX_PAGES_DEFAULT) -> None:
    """Main collection function - fetches all transactions from start date."""
    print(f"[{datetime.now()}] Starting data collection...")
    print(f"Collecting all transactions since {DATA_START_DATE}")
    init_db()
    db = SessionLocal()

    try:
        total_fetched = 0
        total_stored = 0
        page = 1

        while page <= max_pages:
            print(f"\nPage {page}/{max_pages}...")

            data = fetch_transactions_page(page=page, per_page=PAGINATION_SIZE)

            if not data:
                print("  No data returned, stopping")
                break

            transactions = data.get(FIELD_DATA, [])

            if not transactions:
                print("  No more transactions")
                break

            total_fetched += len(transactions)
            print(f"  Fetched {len(transactions)} transactions")

            stored = store_transactions(db, transactions)
            total_stored += stored
            print(f"  Stored {stored} new transactions (total stored: {total_stored})")

            page += 1

            time.sleep(API_RATE_LIMIT_DELAY)

        print(f"\n{'=' * 60}")
        print(f"Total fetched: {total_fetched}")
        print(f"Total stored: {total_stored}")

        print("\nUpdating slippage cache...")
        update_slippage_cache(db)

        print(f"[{datetime.now()}] Data collection completed")

    except Exception as e:
        print(f"Error during collection: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    collect_data(max_pages=MAX_PAGES_DEFAULT)
