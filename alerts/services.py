import requests
import logging
from decimal import Decimal
from .models import StockPrice, Alert
from django.utils import timezone
from django.db.models import Q, Min, Max

STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "META", "NVDA", "NFLX", "INTC", "AMD"
]

API_KEY = "nqXx8pyl9VFIidXkbptZh0KI9IATdMgJ"
BASE_URL = "https://financialmodelingprep.com/api/v3/quote/"

def fetch_stock_prices():
    """
    Fetch latest stock prices from external API.
    Returns a list of price data dicts.
    """
    symbols_str = ",".join(STOCK_SYMBOLS)
    url = f"{BASE_URL}{symbols_str}?apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            logging.error(f"Unexpected API response: {data}")
            return []
        return data
    except Exception as e:
        logging.error(f"Error fetching stock prices: {e}")
        return []

def check_threshold_condition(alert, latest_price):
    """
    Check if the alert condition is currently true (above/below).
    """
    price = Decimal(str(latest_price))
    target = Decimal(str(alert.target_price))
    if alert.condition == 'above':
        return price >= target
    else:
        return price <= target
    
    # return False

def check_threshold_alert(alert, latest_price):
    """
    Check if a threshold alert should be triggered.
    """
    return check_threshold_condition(alert, latest_price)

def evaluate_duration_alert(alert, latest_price):
    """
    Evaluate and update the duration alert's start_time.
    Returns True if the alert should be triggered.
    """
    now = timezone.now()
    condition_true = check_threshold_condition(alert, latest_price)

    # If condition is true, set start_time if not already set
    if condition_true:
        if alert.start_time is None:
            alert.start_time = now
            alert.save(update_fields=["start_time"])
        # If duration has passed since start_time, trigger
        elif (now - alert.start_time).total_seconds() >= alert.duration_minutes * 60:
            return True
    else:
        # Condition is false, reset start_time
        if alert.start_time is not None:
            alert.start_time = None
            alert.save(update_fields=["start_time"])
    return False
