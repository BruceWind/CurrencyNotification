# CurrencyNotification

Monitors AUD/CNY and GBP/CNY exchange rates and sends a Telegram alert when the current price moves into historically extreme territory (top or bottom of the last 3 years of monthly averages).

## How it works

1. Fetches 3 years of daily price history for each currency pair via [yfinance](https://github.com/ranaroussi/yfinance).
2. Calculates the average closing price for every calendar month and sorts those values.
3. Compares today's price against the sorted monthly averages:
   - Price **≥ all-time monthly max** → ALERT (consider selling)
   - Price **≥ 3rd-highest monthly avg** → NOTICE (upper range)
   - Price **≤ all-time monthly min** → ALERT (consider buying)
   - Price **≤ 3rd-lowest monthly avg** → NOTICE (lower range)
4. Sends any triggered message to a Telegram chat, then exits.

## Requirements

- Python 3.10+
- A Telegram bot token and chat ID (see setup below)

## Setup

### 1. Clone and enter the repo

```bash
git clone https://github.com/your-user/CurrencyNotification.git
cd CurrencyNotification
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Copy the example env file and fill in your Telegram details:

```bash
cp .env.example .env
```

Edit `.env`:

```
TELEGRAM_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_CHAT_ID=987654321
```

- **TELEGRAM_TOKEN** – get this from [@BotFather](https://t.me/BotFather) after creating a bot.
- **TELEGRAM_CHAT_ID** – your personal or group chat ID. You can retrieve it by messaging [@userinfobot](https://t.me/userinfobot).

> If `.env` is missing or the values are empty the script still runs and prints alerts to stdout instead of sending them.

## Usage

```bash
python main.py
```

Example output:

```
CurrencyNotification starting ...

Checking AUD2CNY (AUDCNY=X) ...
  Current price       : 4.7123
  Historical max avg  : 5.1042
  3rd-highest avg     : 4.9876
  Historical min avg  : 4.3201
  3rd-lowest avg      : 4.4512
  No alert: price is within the normal historical range.

Checking GBP2CNY (GBPCNY=X) ...
  Current price       : 9.2340
  Historical max avg  : 9.1800
  ...
  [Telegram sent] [GBP2CNY] ALERT: price 9.2340 >= historical MAX monthly avg 9.1800. Consider selling.

All checks complete. Exiting.
```

## Adding more currency pairs

Open `main.py` and add entries to the `CURRENCIES` dict. The keys are display names and the values are [Yahoo Finance ticker symbols](https://finance.yahoo.com/currencies/):

```python
CURRENCIES: dict[str, str] = {
    "AUD2CNY": "AUDCNY=X",
    "GBP2CNY": "GBPCNY=X",
    "EUR2CNY": "EURCNY=X",   # example addition
}
```

## Deploying to Railway (recommended)

[Railway](https://railway.com) runs the script on a schedule with no server to manage. The repo already includes a `railway.toml` that runs the check at 09:00 UTC, Monday through Thursday.

### Steps

1. Push this repo to GitHub.
2. Go to [railway.com](https://railway.com) → **New Project** → **Deploy from GitHub repo** → select this repo.
3. Once the service is created, open its **Variables** tab and add:

   | Key | Value |
   |---|---|
   | `TELEGRAM_TOKEN` | your bot token |
   | `TELEGRAM_CHAT_ID` | your chat ID |

4. Railway will detect `railway.toml` automatically. The service type will be **Cron** and it will run `python main.py` every day at 09:00 UTC.

To change the schedule, edit `cronSchedule` in `railway.toml` using standard cron syntax — for example `"0 1 * * 1-4"` for 01:00 UTC Monday–Thursday.

> The script calls `sys.exit(0)` when finished, which is required for Railway cron jobs to register a successful run.

## Automating locally with cron

If you prefer to run it on your own machine instead:

```bash
crontab -e
```

Add:

```
0 9 * * * /path/to/.venv/bin/python /path/to/CurrencyNotification/main.py
```
