import os
import requests
from dotenv import load_dotenv
from src.const import DATA_START_DATE, PAGINATION_SIZE

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")


def fetch_transactions_page(page: int = 1, per_page: int = PAGINATION_SIZE) -> dict | None:
    """Fetch one page of transactions from the API."""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    params = {
        "page": page,
        "perPage": per_page,
        "startTimestamp": f"{DATA_START_DATE}T00:00:00Z",
        "statuses": "SUCCESS",
    }

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
