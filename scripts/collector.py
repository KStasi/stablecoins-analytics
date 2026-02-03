import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db
from src.api_client import fetch_transactions_page
from src.transaction_service import store_transactions, get_oldest_transaction_timestamp
from src.cache_service import update_slippage_cache
from src.const import (
    PAGINATION_SIZE,
    API_RATE_LIMIT_DELAY,
    DATA_START_DATE,
    FIELD_CREATED_AT,
)


def collect_data() -> None:
    """Main collection function - fetches all transactions from start date."""
    print(f"[{datetime.now()}] Starting data collection...")
    print(f"Collecting all transactions since {DATA_START_DATE}")
    init_db()
    db = SessionLocal()

    try:
        total_fetched = 0
        total_stored = 0
        page = 1

        # Resume from oldest transaction to continue fetching older data
        end_timestamp = get_oldest_transaction_timestamp(db)
        if end_timestamp:
            print(f"Resuming from oldest transaction timestamp: {end_timestamp}...")
        else:
            print("No existing transactions, starting from scratch")

        while True:
            print(f"\nPage {page}...")

            data = fetch_transactions_page(
                per_page=PAGINATION_SIZE, end_timestamp=end_timestamp
            )

            if not data:
                print("  No data returned, stopping")
                break

            transactions = data if isinstance(data, list) else []

            if not transactions:
                print("  No more transactions")
                break

            total_fetched += len(transactions)
            print(f"  Fetched {len(transactions)} transactions")

            stored = store_transactions(db, transactions)
            total_stored += stored
            print(f"  Stored {stored} new transactions (total stored: {total_stored})")

            # Get end_timestamp for next page from the last transaction
            if len(transactions) < PAGINATION_SIZE:
                print("  Reached end of data")
                break

            last_tx = transactions[-1]
            created_at_str = last_tx.get(FIELD_CREATED_AT)
            if not created_at_str:
                print("  No timestamp found in last transaction, stopping")
                break

            end_timestamp = datetime.fromisoformat(
                created_at_str.replace("Z", "+00:00")
            )

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
    collect_data()
