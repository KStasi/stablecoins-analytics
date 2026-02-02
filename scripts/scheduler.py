import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import schedule
from scripts.collector import collect_data
from src.const import COLLECTION_INTERVAL_HOURS, SCHEDULER_SLEEP_SECONDS


def main() -> None:
    """Run the scheduler."""
    schedule.every(COLLECTION_INTERVAL_HOURS).hours.do(collect_data)

    print(
        f"Scheduler started. Will run data collection every {COLLECTION_INTERVAL_HOURS} hours."
    )
    print("Running initial collection...")
    collect_data()

    print("Waiting for next scheduled run...")
    while True:
        schedule.run_pending()
        time.sleep(SCHEDULER_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
