
DEBUG_TICKERS = ["BA260618C235", "AAPL", "CTRA", "FSNGX", "ORCX", "AGQ260320C300", "AAA", "MSFT", "KO"]
error_tickers = ['avxx', 'bmnz', 'hmy', 'orcl', 'orcx']

YAHOO_USEFUL_FIELDS = [

    # Price
    "price",
    # "regularMarketPrice",
    "previousClose",

    # Volume
    "volume",
    "averageVolume",

    # Trend
    "fiftyDayAverage",
    "twoHundredDayAverage",

    # Range
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",

    # Fundamentals
    "marketCap",
    "trailingPE",
    "forwardPE",
    "earningsGrowth",
    "revenueGrowth",
    "profitMargins",
    "debtToEquity",
]
from dataclasses import dataclass
from typing import Any, Callable
HIST_PORT = 65434
CURR_PORT = 65435

def to_float(v):
    if v in (None, "", "None", "N/A"):
        return None
    return float(v)


def to_int(v):
    if v in (None, "", "None", "N/A"):
        return None
    return int(float(v))


def to_str(v):
    if v in (None, "", "None", "N/A"):
        return None
    return str(v)


@dataclass(frozen=True)
class FieldSpec:
    attr: str
    redis_key: str
    converter: Callable[[Any], Any]


MARKET_FIELD_SPECS = [
    FieldSpec("ticker", "ticker", to_str),
    FieldSpec("price", "price", to_float),
    # FieldSpec("regularMarketPrice", "regularMarketPrice", to_float),
    FieldSpec("previousClose", "previousClose", to_float),
    FieldSpec("trailingPE", "trailingPE", to_float),
    FieldSpec("forwardPE", "forwardPE", to_float),
    FieldSpec("pegRatio", "pegRatio", to_float),
    FieldSpec("trailingPegRatio", "trailingPegRatio", to_float),
    FieldSpec("dividendYield", "dividendYield", to_float),
    FieldSpec("returnOnEquity", "returnOnEquity", to_float),
    FieldSpec("debtToEquity", "debtToEquity", to_float),
    FieldSpec("marketCap", "marketCap", to_int),
    FieldSpec("volume", "volume", to_int),
    FieldSpec("averageVolume", "averageVolume", to_int),
    FieldSpec("beta", "beta", to_float),
    FieldSpec("profitMargins", "profitMargins", to_float),
    FieldSpec("operatingMargins", "operatingMargins", to_float),
    FieldSpec("revenueGrowth", "revenueGrowth", to_float),
    FieldSpec("earningsGrowth", "earningsGrowth", to_float),
    FieldSpec("sector", "sector", to_str),
    FieldSpec("industry", "industry", to_str),
    FieldSpec("avg_daily_swing", "avg_daily_swing", to_float),
    FieldSpec("max_swing", "max_swing", to_float),
    FieldSpec("direction_flips", "direction_flips", to_int),
    FieldSpec("is_yoyo", "is_yoyo", to_int),
]
