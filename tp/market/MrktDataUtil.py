import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import pandas as pd

from base_lib.core.base_classes import BaseObject, BaseBool
from base_lib.core.files_include import weekly_fundamentals_file_debug, stock_fundamentals_file, my_symbol_xls_file, \
    prep_ticker_list
from tp.market.mrkt_data_client import get_ticker_info
from tp.market.mrkt_data_updater import DEBUG_TICKERS

from tp.market.validate_ticker import _validate_ticker, ignore_ticker
from tp.market.yahoo_based_info import getHistoricalData
from tp.lib.mrkt_include import MARKET_FIELD_SPECS

RefreshInterval = 7

import builtins
print = builtins.print


def prep_debug_list():
    df_my = pd.read_excel(my_symbol_xls_file)
    tickers = df_my.iloc[:, 0].dropna().unique().tolist()
    tickers = sorted(tickers)
    return tickers

def getTickerInfo(tkr):
    if ignore_ticker(tkr):
        return None
    try:
        mrk_data = MarketDataForTickerRedis(tkr)
        if not mrk_data:
            print("Error getting info for ", tkr)
            return None
        if mrk_data.info:
            return mrk_data
        else:
            return None
    except:
        print("Error getting info for ", tkr)
        return None

@dataclass
class MarketDataHistory(BaseObject):
    tickers: Any = None
    history_data: Any = None
    debug: BaseBool = None

    def isFileOlderThan(self, file_path, days=7):
        if not os.path.exists(file_path):
            return True
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
        return file_age.days > days

    def __post_init__(self):
        super().__post_init__()
        # debug = kwargs.pop('debug', None)
        if self.debug:
            self.tickers = DEBUG_TICKERS
        else:
            self.tickers = prep_ticker_list()

        self.tickers = [tkr for tkr in self.tickers if _validate_ticker(tkr)]
        self.history_data = getHistoricalData(self.tickers)
        return

    def getTickers(self):
        return self.tickers
    def getHistoricalData(self):
        return self.history_data
    def getTickerHistBaseData(self, tkr):
        if self.getHistoricalData() is None:
            return None
        hdata = self.history_data[tkr]
        if hdata is None:
            return None
        tmp = hdata.dropna().tail(2)
        if len(tmp) < 2:
            return None
        return hdata
    def getRSI(self, tkr):
        try:
            df = self.getTickerHistBaseData(tkr)
            if df is None:
                return None
            rsi = _get_rsi(df)
            return rsi
        except Exception as e:
            print(f"Error processing {tkr}: {e}")
        return None

    def getWeeklyInfo(self, save_file='fundamentals_weekly.csv'):
        if self.debug:
            save_file = weekly_fundamentals_file_debug

        if not self.isFileOlderThan(save_file):
            print(f"File {save_file} is not older than {RefreshInterval} days. Skipping refresh.")
            df = pd.read_csv(save_file)
            return df

        print(f"File {save_file} does not exist or is older than {RefreshInterval} days. Refreshing...")
        df = self.refreshWeeklyInfo(save_file=save_file)
        return df

            # return self.refreshWeeklyInfo(save_file=save_file)
    def refreshWeeklyInfo(self, save_file='fundamentals_weekly.csv'):
        records = []
        print("downloading Weekly data ")
        cnt = 0
        tickers = self.getTickers()
        for t in tickers:
            cnt += 1
            if cnt >= 100:
                print(cnt)
                cnt = 0
            else:
                print(".", end="", flush=True)
            tiObj = getTickerInfo(t)
            if tiObj is None:
                continue
            bvps = None
            if tiObj.book_value is not None and tiObj.shares is not None and tiObj.shares > 0:
                bvps = tiObj.book_value
            records.append({
                'Ticker': t,
                'Sector': tiObj.sector,
                'BVPS': bvps,
                'Growth': tiObj.growth,
                'Date': datetime.now().strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(records)
        # Save snapshot (append or overwrite)
        df.to_csv(save_file, index=False)
        print(f"\nSaved {save_file}")
        return df
    def prepareRealtimeData(self, tickers=None):
        if tickers is None:
            tickers = self.getTickers()
        data = {}
        for t in tickers:
            data[t] = self.getTickerData(t)
        return data


def to_float(v):
    if v in ("", None):
        return None
    return float(v)

@dataclass
class MarketDataForTickerRedis(BaseObject):
    ticker: str
    price: float = None
    pe: float = None
    yield_pct: float = None
    def __post_init__(self):
        pass
    @classmethod
    def from_redis(cls, d: dict):
        return cls(
            ticker=d["ticker"],
            price=to_float(d["price"]),
            pe=to_float(d["trailingPE"]),
            yield_pct=to_float(d["dividendYield"]),
        )

@dataclass
class MarketDataForTickerRedis(BaseObject):
    ticker: str | None = None
    price: float | None = None
    # regularMarketPrice: float | None = None
    previousClose: float | None = None
    trailingPE: float | None = None
    forwardPE: float | None = None
    pegRatio: float | None = None
    trailingPegRatio: float | None = None
    dividendYield: float | None = None
    returnOnEquity: float | None = None
    debtToEquity: float | None = None
    marketCap: int | None = None
    volume: int | None = None
    averageVolume: int | None = None
    beta: float | None = None
    profitMargins: float | None = None
    operatingMargins: float | None = None
    revenueGrowth: float | None = None
    earningsGrowth: float | None = None
    sector: str | None = None
    industry: str | None = None
    avg_daily_swing: float | None = None
    max_swing: float | None = None
    direction_flips: int | None = None
    is_yoyo: int | None = None

    @classmethod
    def from_redis(cls, d: dict) -> "BaseMarketData":
        kwargs = {
            spec.attr: spec.converter(d.get(spec.redis_key))
            for spec in MARKET_FIELD_SPECS
        }
        return cls(**kwargs)

from ta.momentum import RSIIndicator
RSI_WINDOW = 14
def _get_rsi(df):
    # df = data[ticker].dropna()
    if len(df) < RSI_WINDOW + 1:
        return None
    rsi = RSIIndicator(df['Close'], window=RSI_WINDOW).rsi().iloc[-1]
    return rsi

def _rawToObj(rawdata)->MarketDataForTickerRedis:
    md = MarketDataForTickerRedis.from_redis(rawdata)
    return md

def get_ticker_data(ticker_symbol)->MarketDataForTickerRedis:
    info = get_ticker_info(ticker_symbol)
    if info:
        tkrObj = _rawToObj(info)
        return tkrObj
    return None

# To support current usage - need to retire soon
def get_market_price(ticker_symbol):
    info = get_ticker_data(ticker_symbol)
    if info:
        return info.price
    return 0

if __name__ == '__main__':
    print("test")
    for t in DEBUG_TICKERS:
        print(t, get_market_price(t))
        tkrObj = get_ticker_data(t)
        if not tkrObj:
            continue
        tkrObj.pretty_print_members()

    mrk_data = MarketDataHistory(debug=True)
    mrk_data.refreshWeeklyInfo(save_file=weekly_fundamentals_file_debug)
    for t in mrk_data.getTickers():
        rsi = mrk_data.getRSI(t)
        print(f"{t} RSI: {rsi}")
    mrk_data.getWeeklyInfo(save_file=stock_fundamentals_file)

