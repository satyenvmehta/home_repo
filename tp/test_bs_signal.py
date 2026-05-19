import pandas as pd


# =========================================================
# SAMPLE TRADE DATA
# =========================================================

df = pd.DataFrame([
    # -----------------------------------------------------
    # Scenario 1
    # Latest day has BOTH BUY and SELL
    # -----------------------------------------------------
    {"ticker": "SSS", "trade_date": "2026-05-15", "qty": 10, "price": 100},
    {"ticker": "SSS", "trade_date": "2026-05-15", "qty": 10, "price": 120},

    # -----------------------------------------------------
    # Scenario 1
    # Latest day has BOTH BUY and SELL
    # -----------------------------------------------------
    {"ticker": "AAA", "trade_date": "2026-05-15", "qty":  10, "price": 100},
    {"ticker": "AAA", "trade_date": "2026-05-15", "qty": -10, "price": 120},

    # -----------------------------------------------------
    # Scenario 2
    # Latest day has ONLY BUY
    # Fallback to overall highest sell
    # -----------------------------------------------------
    {"ticker": "BBB", "trade_date": "2026-05-10", "qty": -10, "price": 140},
    {"ticker": "BBB", "trade_date": "2026-05-15", "qty":  20, "price": 100},

    # -----------------------------------------------------
    # Scenario 3
    # Latest day has ONLY SELL
    # Fallback to overall lowest buy
    # -----------------------------------------------------
    {"ticker": "CCC", "trade_date": "2026-05-01", "qty":  10, "price": 90},
    {"ticker": "CCC", "trade_date": "2026-05-15", "qty": -10, "price": 130},

    # -----------------------------------------------------
    # Scenario 4
    # Multiple BUYs same latest day
    # Use LOWEST BUY
    # -----------------------------------------------------
    {"ticker": "DDD", "trade_date": "2026-05-15", "qty":  10, "price": 100},
    {"ticker": "DDD", "trade_date": "2026-05-15", "qty":  20, "price": 95},
    {"ticker": "DDD", "trade_date": "2026-05-15", "qty": -10, "price": 125},

    # -----------------------------------------------------
    # Scenario 5
    # Multiple SELLs same latest day
    # Use HIGHEST SELL
    # -----------------------------------------------------
    {"ticker": "EEE", "trade_date": "2026-05-15", "qty":  10, "price": 100},
    {"ticker": "EEE", "trade_date": "2026-05-15", "qty": -10, "price": 118},
    {"ticker": "EEE", "trade_date": "2026-05-15", "qty": -20, "price": 130},

    # -----------------------------------------------------
    # Scenario 6
    # HOLD scenario
    # -----------------------------------------------------
    {"ticker": "FFF", "trade_date": "2026-05-15", "qty":  10, "price": 100},
    {"ticker": "FFF", "trade_date": "2026-05-15", "qty": -10, "price": 110},

    # -----------------------------------------------------
    # Scenario 1
    # Latest day has BOTH BUY and SELL
    # -----------------------------------------------------
    {"ticker": "GGG", "trade_date": "2026-05-15", "qty": 10, "price": 100},
    {"ticker": "GGG", "trade_date": "2026-05-15", "qty": 10, "price": 120},

    # -----------------------------------------------------
    # Scenario 1
    # Latest day has BOTH BUY and SELL
    # -----------------------------------------------------
    {"ticker": "HHH", "trade_date": "2026-05-15", "qty": -10, "price": 100},
    {"ticker": "HHH", "trade_date": "2026-05-15", "qty": -10, "price": 120},
    # -----------------------------------------------------
    # Scenario 1
    # Latest day has BOTH BUY and SELL
    # -----------------------------------------------------
    {"ticker": "III", "trade_date": "2026-05-15", "qty": -10, "price": 100},
    {"ticker": "III", "trade_date": "2026-05-15", "qty": -10, "price": 120},

])


# =========================================================
# CURRENT MARKET PRICES
# =========================================================

current_prices = {
    "AAA": 135,   # SELL
    "BBB": 85,    # BUY
    "CCC": 150,   # SELL
    "DDD": 80,    # BUY
    "EEE": 150,   # SELL
    "FFF": 105,   # HOLD
    "SSS" : 80,   # BUY
    "GGG" : 150,   # SELL
    "HHH" : 150,   # SELL
    "III" : 80,   # BUY
    "JJJ" : 150,   # SELL
    "KKK" : 80,   # BUY
    "LLL" : 150,   # SELL

}


# =========================================================
# REFERENCE + SIGNAL LOGIC
# =========================================================
def get_trade_refs(df, ticker):
    d = df[df["ticker"] == ticker].copy()
    d["trade_date"] = pd.to_datetime(d["trade_date"])

    latest_date = d["trade_date"].max()
    latest_day = d[d["trade_date"] == latest_date]

    has_buy = (latest_day["qty"] > 0).any()
    has_sell = (latest_day["qty"] < 0).any()

    if has_buy and has_sell:
        buy_ref = latest_day[latest_day["qty"] > 0]["price"].min()
        sell_ref = latest_day[latest_day["qty"] < 0]["price"].max()

    elif has_buy and not has_sell:
        buy_ref = latest_day[latest_day["qty"] > 0]["price"].min()
        sell_ref = buy_ref

    elif has_sell and not has_buy:
        sell_ref = latest_day[latest_day["qty"] < 0]["price"].max()
        buy_ref = sell_ref

    else:
        buy_ref = None
        sell_ref = None

    return buy_ref, sell_ref

def get_signal(cp, buy_ref, sell_ref):
    if sell_ref is not None and cp > sell_ref * 1.10:
        return "SELL"

    if buy_ref is not None and cp < buy_ref * 0.90:
        return "BUY"

    return "HOLD"


# =========================================================
# EXECUTION
# =========================================================

results = []

for ticker in current_prices:

    cp = current_prices[ticker]

    buy_ref, sell_ref = get_trade_refs(df, ticker)

    signal = get_signal(cp, buy_ref, sell_ref)

    results.append({
        "ticker": ticker,
        "current_price": cp,
        "buy_ref": buy_ref,
        "sell_ref": sell_ref,
        "signal": signal
    })


result_df = pd.DataFrame(results)

print(result_df)