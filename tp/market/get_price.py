# import common_include as C
from pandas.core.frame import DataFrame

from base_lib.core.base_classes import sleep_sec
# import time

from tp.market.MrktDataUtil import MarketDataForTicker, getTickerObj, getHistoricalData, getTickerInfo
# from tp.market.MrktDataUtil import  getTickerObj
from tp.market.validate_ticker import ignore_ticker


# def _getTickerObj(tkr_in):
#     try:
#         tkr = yf.Ticker(tkr_in)
#         return tkr
#     except:
#         sleep_sec(1)
#         return None
#
# def getTickerObj(tkr):
#     tries = 0
#     while tries < 3:
#         tries += 1
#         tkr = _getTickerObj(tkr)
#         if tkr:
#             break
#     return tkr
#
# pct_cols = [
#     "ROE",
#     "DividendYield",
#     "ProfitMargin",
#     "OperatingMargin",
#     "RevenueGrowth",
#     "EarningsGrowth",
# ]
# @C.dataclass
# class MarketDataForTicker(C.BaseObject):
#     ticker: str
#     info: dict = None
#     sector: str = None # = info.get('sector')
#     book_value: float = None # = info.get('bookValue')  # may represent equity per share or total
#     shares: int = None # = info.get('sharesOutstanding')
#     growth: float = None # = info.get('earningsQuarterlyGrowth')
#     quoteType : str = None # = info.get('quoteType')
#     PE : float = None # = info.get('trailingPE')
#     ForwardPE : float = None # = info.get('forwardPE')
#     DividendYield : float = None # = info.get('dividendYield')
#     ROE : float = None # = info.get('returnOnEquity')
#     PEG : float = None # = info.get('pegRatio')
#     ProfitMargin : float = None # = info.get('profitMargins')
#     OperatingMargin : float = None # = info.get('operatingMargins')
#     RevenueGrowth : float = None # = info.get('revenueGrowth')
#     EarningsGrowth : float = None # = info.get('earningsGrowth')
#     MarketCap : float = None # = info.get('marketCap')
#     RSI : float = None
#     def __post_init__(self):
#         self.tkrObj = getTickerObj(self.ticker)
#         if not self.tkrObj:
#             print("Error getting ticker object for ", self.ticker)
#             return None
#         self.info = self.tkrObj.info
#         if self.info:
#             self.sector = self.info.get('sector')
#             self.book_value = self.info.get('bookValue')
#             self.shares = self.info.get('sharesOutstanding')
#             self.growth = self.info.get('earningsQuarterlyGrowth')
#             self.quoteType = self.info.get('quoteType')
#             self.PE = self.info.get('trailingPE')
#             self.ForwardPE = self.info.get('forwardPE')
#             self.DividendYield = self.info.get('dividendYield')
#             self.ROE = self.info.get('returnOnEquity') *100
#             self.PEG = self.info.get('pegRatio')
#             self.ProfitMargin = self.info.get('profitMargins')
#             self.RevenueGrowth = self.info.get('revenueGrowth')
#             self.EarningsGrowth = self.info.get('earningsGrowth')
#             self.MarketCap = self.info.get('marketCap')
#             self.DebtToEquity = self.info.get('debtToEquity')
#             self.high_quality = self._high_quality()
#         return
#
#     def _high_quality(self):
#         if self.quoteType == 'EQUITY':
#             if self.sector and self.book_value and self.shares and self.growth:
#                 if self.ROE > 15 and self.ProfitMargin > .1 and self.PEG < 1.5 and self.DebtToEquity < 1.0:
#                     if self.EarningsGrowth > .1 and self.RevenueGrowth > .1:
#                         if self.MarketCap > 1000000000:
#                             print("High Quality Ticker ", self.ticker)
#                             return True
#         return False
#
#     def setRSI(self, rsi):
#         self.RSI = rsi
#         return


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

def get_quote_type_based_price(tkrObj:MarketDataForTicker):
    qt = tkrObj.info['quoteType']
    if qt == 'ETF':
        return tkrObj.info['ask']
    elif qt == 'MUTUALFUND':
        return tkrObj.info['regularMarketPrice']
    elif qt == 'EQUITY':
        return tkrObj.info['regularMarketPrice']
    else:
        return tkrObj.info['currentPrice']
    return None

def _get_market_tkr_obj(ticker_symbol) -> MarketDataForTicker:
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
        # price = get_quote_type_based_price(tkr)
        tkrObj = tkr

    except Exception as e:
        print(e)
        if q_type:
            print(q_type, ticker_symbol )
        tkrObj = None
    finally:
        current_tkr_obj = tkrObj
        # current_price = price
        # tkr_list.append(ticker_symbol)
        # tkr_dict[ticker_symbol] = current_price
    return current_tkr_obj

def get_market_tkr_obj(ticker_symbol) -> MarketDataForTicker:
    if len(ticker_symbol) > len('G637AM'):
        return None
    current_tkr_obj = _get_market_tkr_obj(ticker_symbol)
    tryal = 0
    while current_tkr_obj is None:
        sleep_sec(1)
        current_tkr_obj = _get_market_tkr_obj(ticker_symbol)
        print({"trying for same ticker" : ticker_symbol})
        tryal += 1
        if tryal > 3:
            break
    return current_tkr_obj

# To support current usage - need to retire soon
def get_market_price(ticker_symbol):
    tkrObj = get_market_tkr_obj(ticker_symbol)
    if tkrObj:
        return get_quote_type_based_price(tkrObj)
    return 0

def get_market_price_for_list(ticker_symbol_list):
    for ticker_symbol in ticker_symbol_list:
        price = get_market_price(ticker_symbol)
        print({ticker_symbol: price})

def prepare_final_mrktdata_obj():
    pass

def getMarketCurrentAndHistory(tkr_list):
    hist_data = getHistoricalData(tkr_list)
    current_data = {}
    for tkr in tkr_list:
        current_data[tkr] = get_market_tkr_obj(tkr)
    return current_data, hist_data


if __name__ == "__main__":
    # sleep_sec(10)
    t = ['ILTB', 'SNDK', 'SPHIX', 'OKTA',  'ARKK', 'AAPL', 'T']
    get_market_price_for_list(t)
    hist_data = getHistoricalData(t)
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
