import common_include as C
import yfinance as yf
from pandas.core.frame import DataFrame

import time

from tp.market.validate_ticker import ignore_ticker


def sleep_sec(s):
    time.sleep(s)
    return

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

@C.dataclass
class MarketData(C.BaseObject):
    ticker: str
    info: dict = None
    sector: str = None # = info.get('sector')
    book_value: float = None # = info.get('bookValue')  # may represent equity per share or total
    shares: int = None # = info.get('sharesOutstanding')
    growth: float = None # = info.get('earningsQuarterlyGrowth')
    quoteType : str = None # = info.get('quoteType')
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
        return

def getTickerInfo(tkr):
    if ignore_ticker(tkr):
        return None
    try:
        mrk_data = MarketData(tkr)
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

def getTkrHist(tkr):
    tkr = getTickerObj(tkr)
    if tkr:
        hist = tkr.history(period='1y', interval='1d', start=None, end=None)
        if isinstance(hist, DataFrame):
            if not hist.empty:
                return hist
    return None

sl = 0
tkr_list = []
tkr_dict = {}
def _get_market_price_1(ticker_symbol):
    price = 0
    if ticker_symbol in tkr_list:
        price = tkr_dict[ticker_symbol]
        # print("Return from memory ", ticker_symbol, price)
        return price
    tkr = getTickerObj(ticker_symbol)
    max_sl = 2
    q_type = None
    try:
        global sl
        sl = sl + 1
        if sl > max_sl:
            print("sleep ", sl)
            sleep_sec(1)
            sl = 0
        q_type = tkr.info['quoteType']
        price = 0
        if q_type == 'ETF':
            price = tkr.info['ask']
        elif q_type == 'MUTUALFUND':
            price = tkr.info['regularMarketPrice']
        elif q_type == 'EQUITY':
            price = tkr.info['regularMarketPrice']
        else:
            price = tkr.info['currentPrice']
    except Exception as e:
        print(e)
        if q_type:
            print(q_type, ticker_symbol )
        price = -1
    finally:
        current_price = price
        tkr_list.append(ticker_symbol)
        tkr_dict[ticker_symbol] = current_price
    return current_price

def get_market_price(ticker_symbol):
    if len(ticker_symbol) > len('G637AM'):
        return 0
    current_price = -1
    current_price = _get_market_price_1(ticker_symbol)
    tryal = 0
    while current_price < 0:
        sleep_sec(1)
        current_price = _get_market_price_1(ticker_symbol)
        print({"trying for same ticker" : ticker_symbol})
        tryal += 1
        if tryal > 3:
            break
    return current_price

# def _get_market_price(ticker_symbol):
#     # Download the most recent data (intraday data)
#     current_price = 0
#     try:
#         tkr = yf.download(ticker_symbol, period="1d", interval="1m")
#         found = True
#     except:
#         found = None
#     finally:
#         if found:
#             if isinstance(tkr, DataFrame):
#                 if not tkr.empty:
#                     pprint(type(tkr))
#                     current_price = tkr['Close'].iloc[-1]
#         # Access the current closing price (assuming you downloaded recent data)
#         # You can access other data points like 'Open', 'High', 'Low', etc.
#                     print(f"Current Price of {ticker_symbol}: {current_price}")
#
#         return str(current_price)

def getHistoricalData(tickers):
    if not isinstance(tickers, list):
        return False
    print("downloading data for ", tickers)
    print("Total tickers ....",  len(tickers))
    data = yf.download(tickers, period="30d", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    print("download complete")
    return data

if __name__ == "__main__":
    # sleep_sec(10)
    t = ['ILTB', 'SNDK', 'SPHIX', 'OKTA', 'G637AM102', 'ARKK', 'AAPL', 'T']
    getHistoricalData(t)
    for i in [1,2,3,4,5,6,7,8,9,10]:
        for l in t:
            # print({l: get_market_price(l)})
            tiObj = getTickerInfo(l)
            if tiObj:
                for name, value in tiObj.__dict__.items():
                    if name in ['tkrObj', 'info']:
                        continue
                    print(f"{name}: {value}")
                print("\n")
            sleep_sec(1)

    # print((get_market_price('G637AM102')))
    # print(get_market_price("ARKK"))
    # print(get_market_price('AAPL'))
    # print(getTkrHist('MSFT'))
    print("Done")



# def get_historical_price(ticker_symbol):
#     # Download the historical data for the ticker symbol
#     tkr = yf.Ticker(ticker_symbol)
#     hist = tkr.history(period="1d")
#     # Access the 'Close' column of the historical data
#     if isinstance(hist, DataFrame):
#         if not hist.empty:
#             current_price = hist['Close'].iloc[-1]
#             print(f"Current Price of {ticker_symbol}: {current_price}")
#             return current_price
#     return None