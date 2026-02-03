import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.const import API_URL, DATA_START_DATE, PAGINATION_SIZE

load_dotenv()

API_KEY = os.getenv("API_KEY")


def fetch_transactions_page(
    per_page: int = PAGINATION_SIZE,
    end_timestamp: datetime | None = None,
) -> list | None:
    """Fetch transactions from the API using timestamp-based pagination.

    Args:
        per_page: Number of transactions to fetch (1-1000)
        end_timestamp: Fetch transactions older than this timestamp

    Returns:
        API response list or None on error
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}

    params = {
        "numberOfTransactions": per_page,
        "startTimestamp": f"{DATA_START_DATE}T00:00:00Z",
        "statuses": "SUCCESS",
        "direction": "next",
    }

    if end_timestamp:
        params["endTimestamp"] = end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"  API error: {response.status_code} - {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  Error fetching transactions: {e}")
        return None
