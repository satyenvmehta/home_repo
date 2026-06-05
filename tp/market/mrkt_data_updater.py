import time
import redis

from base_lib.core.base_classes import BaseDate
from tp.lib.mrkt_include import DEBUG_TICKERS
from tp.market.yahoo_based_info import  _getTickerObj
from base_lib.core.files_include import prep_ticker_list

def make_key(ticker: str) -> str:
    return f"mrkt:{ticker}"

DEBUG=False

# Following info resides in Redis server for each ticker received


@staticmethod
def resolve_price(info: dict):
    price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
    )
    return price

def get_quote_type_based_price(info: dict):
    qt = info.get('quoteType')
    if not qt:
        return None
    if qt == 'ETF':
        return info.get('ask')
    elif qt == 'MUTUALFUND':
        return resolve_price(info)
    elif qt == 'EQUITY':
        return resolve_price(info)
    else:
        return resolve_price(info)

critical_fields = ["currentPrice", "trailingPE", "dividendYield", "quoteType", "regularMarketPrice", "ask"]

REQUIRED_FIELDS = [ "quoteType"]
CLENT_FILEDS = ["trailingPE", "dividendYield",]

def has_required_market_data(d: dict) -> bool:
    return any(d.get(field) is not None for field in REQUIRED_FIELDS)


daily_swing_pct_param = 6
def _get_yoyo_metrics(df, no_days=5):
    if df.empty or len(df) < no_days:
        return None

    # 1. Calculate Daily Range Percentage: (High - Low) / Open
    # This measures how much the "Yo-Yo" moved during the day
    df['daily_swing_pct'] = (df['High'] - df['Low']) / df['Open'] * 100

    # 2. Identify Direction: 1 for Green (Close > Open), -1 for Red
    df['direction'] = df.apply(lambda x: 1 if x['Close'] > x['Open'] else -1, axis=1)

    # 3. Count Directional Flips: Does it change color day-to-day?
    df['flip'] = df['direction'].diff().fillna(0).apply(lambda x: 1 if x != 0 else 0)

    # Get the last N business days
    recent_data = df.tail(no_days)
    isYoYo = recent_data['daily_swing_pct'].mean() > daily_swing_pct_param and recent_data['flip'].sum() >= (no_days / 2)
    if isYoYo:
        isYoYo = 1
    else:
        isYoYo = 0
    metrics = {
        # "ticker": ticker_symbol,
        "avg_daily_swing": float(round(recent_data['daily_swing_pct'].mean(), 2)),
        "max_swing": float(round(recent_data['daily_swing_pct'].max(), 2)),
        "direction_flips": int(recent_data['flip'].sum()),
        "is_yoyo": isYoYo
    }

    return metrics

def get_market_data(ticker: str) -> dict:
    # Replace this later with yfinance / API call
    info, hist = _getTickerObj(ticker)
    row = {}

    if not info:
        return None

    if not all(info.get(field) is not None for field in REQUIRED_FIELDS):
        print(f"Missing critical fields for {ticker}: {info}")
        return None

    row["ticker"] = ticker
    row["price"] = get_quote_type_based_price(info)
    for cf in CLENT_FILEDS:
        row[cf] = info.get(cf)

    if not hist.empty:
        yoyo_metrics = _get_yoyo_metrics(hist)
        if yoyo_metrics:
            row.update(yoyo_metrics)
    return row

def main():
    dt = BaseDate()
    print("Starting Market Data Updater at ", dt)
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    tkrList = prep_ticker_list()
    if DEBUG:
        r.flushall()
        print("Cleared Redis")
        print("Populating Redis with market data")
        tkrList = DEBUG_TICKERS

    while True:
        for ticker in tkrList:
            ticker = ticker.strip().upper()
            if not ticker or ticker.startswith("#"):
                continue
            if ticker == "SYMBOL":
                continue
            key = make_key(ticker)
            if r.exists(key) and DEBUG:
                r.delete(key)
            # print("Getting data for:", ticker)
            data = get_market_data(ticker)
            if not data:
                print("No data for:", ticker)
                continue

            clean_data = {
                k: "" if v is None else v
                for k, v in data.items()
            }

            r.hset(key, mapping=clean_data)

            print("Updated:", key, data)

        if DEBUG:
            seconds = 3
        else:
            seconds = 600
        import common_include as C
        print("Last update at ", print(C.date_now()))
        time.sleep(seconds)


if __name__ == "__main__":
    main()