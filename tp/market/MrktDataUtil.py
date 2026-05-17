import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf

from base_lib.core.base_classes import BaseObject, BaseBool, sleep_sec
from base_lib.core.files_include import weekly_fundamentals_file_debug, stock_fundamentals_file, my_symbol_xls_file, \
    sp_500_file, nasd_100_file, ticker_file
# import common_include as C
# from tp.market.get_price import getHistoricalData
# from tp.TradeUtil import  prep_ticker_list, prep_debug_list
# from tp.market.get_price import sleep_sec
from tp.market.validate_ticker import _validate_ticker, ignore_ticker

RefreshInterval = 7

import builtins
print = builtins.print


def get_my_symbols_df():
    return pd.read_excel(my_symbol_xls_file)


def prep_ticker_list():
    # Read both Excel files (assume first column contains tickers)
    df1 = pd.read_excel(sp_500_file)
    df2 = pd.read_excel(nasd_100_file)
    df3 = pd.read_csv(ticker_file)
    df_my = get_my_symbols_df()

    # Combine tickers from both sheets, remove duplicates, drop NaN
    tickers = pd.concat([df1, df2, df3, df_my], ignore_index=True).iloc[:, 0].dropna().unique().tolist()
    # tickers = ['MBLY', 'LMT', 'NGD', 'avxx', 'orcl', 'orcx', 'hmy']
    tickers = sorted(tickers)
    return tickers


def prep_debug_list():
    df_my = get_my_symbols_df()
    tickers = df_my.iloc[:, 0].dropna().unique().tolist()
    tickers = sorted(tickers)
    return tickers

def getTickerInfo(tkr):
    if ignore_ticker(tkr):
        return None
    try:
        mrk_data = MarketDataForTicker(tkr)
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

def getHistoricalData(tickers):
    if not isinstance(tickers, list):
        return False
    print("downloading data for ", tickers)
    print("Total tickers ....",  len(tickers))
    data = yf.download(tickers, period="30d", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    print("download complete")
    return data

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
            self.tickers = prep_debug_list()
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
            # sector = tiObj.get('sector')
            # book_value = tiObj.get('bookValue')  # may represent equity per share or total
            # shares = tiObj.get('sharesOutstanding')
            # growth = tiObj.get('earningsQuarterlyGrowth')  # or another growth metric
            # Compute BVPS if needed
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


def _getTickerObj(tkr_in):
    try:
        tkr = yf.Ticker(tkr_in)
        return tkr
    except:
        sleep_sec(1)
        return None

def getTickerObj(tkr):
    tries = 0
    while tries < 3:
        tries += 1
        tkr = _getTickerObj(tkr)
        if tkr:
            break
    return tkr

pct_cols = [
    "ROE",
    "DividendYield",
    "ProfitMargin",
    "OperatingMargin",
    "RevenueGrowth",
    "EarningsGrowth",
]
@dataclass
class MarketDataForTicker(BaseObject):
    ticker: str
    info: dict = None
    sector: str = None # = info.get('sector')
    book_value: float = None # = info.get('bookValue')  # may represent equity per share or total
    shares: int = None # = info.get('sharesOutstanding')
    growth: float = None # = info.get('earningsQuarterlyGrowth')
    quoteType : str = None # = info.get('quoteType')
    PE : float = None # = info.get('trailingPE')
    ForwardPE : float = None # = info.get('forwardPE')
    DividendYield : float = None # = info.get('dividendYield')
    ROE : float = None # = info.get('returnOnEquity')
    PEG : float = None # = info.get('pegRatio')
    ProfitMargin : float = None # = info.get('profitMargins')
    OperatingMargin : float = None # = info.get('operatingMargins')
    RevenueGrowth : float = None # = info.get('revenueGrowth')
    EarningsGrowth : float = None # = info.get('earningsGrowth')
    MarketCap : float = None # = info.get('marketCap')
    RSI : float = None
    def __post_init__(self):
        self.tkrObj = getTickerObj(self.ticker)
        if not self.tkrObj:
            print("Error getting ticker object for ", self.ticker)
            return None
        self.info = self.tkrObj.info
        if self.info:
            self.sector = self.info.get('sector')
            self.book_value = self.info.get('bookValue')
            self.shares = self.info.get('sharesOutstanding')
            self.growth = self.info.get('earningsQuarterlyGrowth')
            self.quoteType = self.info.get('quoteType')
            self.PE = self.info.get('trailingPE')
            self.ForwardPE = self.info.get('forwardPE')
            self.DividendYield = self.info.get('dividendYield')
            self.ROE = self.info.get('returnOnEquity') *100
            self.PEG = self.info.get('pegRatio')
            self.ProfitMargin = self.info.get('profitMargins')
            self.RevenueGrowth = self.info.get('revenueGrowth')
            self.EarningsGrowth = self.info.get('earningsGrowth')
            self.MarketCap = self.info.get('marketCap')
            self.DebtToEquity = self.info.get('debtToEquity')
            self.high_quality = self._high_quality()
        return

    def _high_quality(self):
        if self.quoteType == 'EQUITY':
            if self.sector and self.book_value and self.shares and self.growth:
                if self.ROE > 15 and self.ProfitMargin > .1 and self.PEG < 1.5 and self.DebtToEquity < 1.0:
                    if self.EarningsGrowth > .1 and self.RevenueGrowth > .1:
                        if self.MarketCap > 1000000000:
                            print("High Quality Ticker ", self.ticker)
                            return True
        return False

    def setRSI(self, rsi):
        self.RSI = rsi
        return

from ta.momentum import RSIIndicator
RSI_WINDOW = 14
def _get_rsi(df):
    # df = data[ticker].dropna()
    if len(df) < RSI_WINDOW + 1:
        return None
    rsi = RSIIndicator(df['Close'], window=RSI_WINDOW).rsi().iloc[-1]
    return rsi

if __name__ == '__main__':
    mrk_data = MarketDataHistory(debug=True)
    mrk_data.refreshWeeklyInfo(save_file=weekly_fundamentals_file_debug)
    for t in mrk_data.getTickers():
        rsi = mrk_data.getRSI(t)
        print(f"{t} RSI: {rsi}")
    mrk_data.getWeeklyInfo(save_file=stock_fundamentals_file)

