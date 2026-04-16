import os
import sys
from datetime import datetime, timedelta

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

CURRENCIES: dict[str, str] = {
    "AUD2CNY": "AUDCNY=X",
    "GBP2CNY": "GBPCNY=X",
    "CAD2CNY": "CADCNY=X",
    "EUR2CNY": "EURCNY=X",
    "USD2CNY": "USDCNY=X",
}

HISTORY_YEARS = 3


def send_telegram(message: str) -> None:
    """Send a message via Telegram Bot API. Prints to stdout if credentials are missing."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"  [Telegram skipped – no credentials] {message}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        timeout=10,
    )
    resp.raise_for_status()
    print(f"  [Telegram sent] {message}")


def fetch_monthly_averages(ticker_symbol: str) -> pd.Series:
    """Download 3 years of daily closes and return monthly averages sorted ascending."""
    end = datetime.today()
    start = end - timedelta(days=365 * HISTORY_YEARS)
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
    )
    if hist.empty:
        raise ValueError(f"No historical data returned for {ticker_symbol}")
    monthly_avg = hist["Close"].resample("ME").mean()
    return monthly_avg.sort_values().reset_index(drop=True)


def get_current_price(ticker_symbol: str) -> float:
    """Return the most recent closing price for a ticker."""
    hist = yf.Ticker(ticker_symbol).history(period="2d")
    if hist.empty:
        raise ValueError(f"Cannot retrieve current price for {ticker_symbol}")
    return float(hist["Close"].iloc[-1])


def check_and_notify(name: str, ticker_symbol: str) -> None:
    print(f"\nChecking {name} ({ticker_symbol}) ...")

    monthly_avg = fetch_monthly_averages(ticker_symbol)
    current = get_current_price(ticker_symbol)
    n = len(monthly_avg)

    max_val = monthly_avg.iloc[-1]
    third_max_val = monthly_avg.iloc[-3] if n >= 3 else monthly_avg.iloc[0]
    min_val = monthly_avg.iloc[0]
    third_min_val = monthly_avg.iloc[2] if n >= 3 else monthly_avg.iloc[-1]

    print(f"  Current price       : {current:.4f}")
    print(f"  Historical max avg  : {max_val:.4f}")
    print(f"  3rd-highest avg     : {third_max_val:.4f}")
    print(f"  Historical min avg  : {min_val:.4f}")
    print(f"  3rd-lowest avg      : {third_min_val:.4f}")

    alerted = False

    if current >= max_val:
        send_telegram(
            f"[{name}] 🔴ALERT: price {current:.4f} >= historical MAX monthly avg "
            f"{max_val:.4f}. Consider selling."
        )
        alerted = True
    elif current >= third_max_val:
        send_telegram(
            f"[{name}]  🟡NOTICE: price {current:.4f} >= 3rd-highest monthly avg "
            f"{third_max_val:.4f}. Price is in upper range."
        )
        alerted = True

    if current <= min_val:
        send_telegram(
            f"[{name}] 🟢ALERT: price {current:.4f} <= historical MIN monthly avg "
            f"{min_val:.4f}. Consider buying."
        )
        alerted = True
    elif current <= third_min_val:
        send_telegram(
            f"[{name}]  🔵NOTICE: price {current:.4f} <= 3rd-lowest monthly avg "
            f"{third_min_val:.4f}. Price is in lower range."
        )
        alerted = True

    if not alerted:
        print("  No alert: price is within the normal historical range.")


def main() -> None:
    print("CurrencyNotification starting ...")

    missing = [name for name, val in [("TELEGRAM_TOKEN", TELEGRAM_TOKEN), ("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)] if not val]
    if missing:
        raise EnvironmentError(f"Required environment variable(s) are not set or empty: {', '.join(missing)}")

    for name, symbol in CURRENCIES.items():
        try:
            check_and_notify(name, symbol)
        except Exception as exc:
            print(f"  Error processing {name}: {exc}")

    print("\nAll checks complete. Exiting.")
    sys.exit(0)


if __name__ == "__main__":
    main()
