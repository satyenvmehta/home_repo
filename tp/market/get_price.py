# import common_include as C
from pandas.core.frame import DataFrame

from base_lib.core.base_classes import sleep_sec
# import time

from tp.market.MrktDataUtil import MarketDataForTicker, getTickerObj, getHistoricalData, getTickerInfo
# from tp.market.MrktDataUtil import  getTickerObj
# from tp.market.validate_ticker import ignore_ticker


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
