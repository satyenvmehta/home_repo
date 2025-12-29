from pprint import pprint

import yfinance as yf
# from time_util import sleep_sec
# from pandas import DataFrame
from pandas.core.frame import DataFrame

import time
def sleep_sec(s):
    time.sleep(s)
    return

def _getTickerObj(tkr_in):
    try:
        tkr = yf.Ticker(tkr_in)
        return tkr
    except:
        return None

def getTickerObj(tkr):
    tries = 0
    while tries < 2:
        tries += 1
        tkr = _getTickerObj(tkr)
        if tkr:
            break
    return tkr

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
        if price > 0:
        # print("Return from memory ", ticker_symbol, price)
            return price
    tkr = getTickerObj(ticker_symbol)
    max_sl = 2
    q_type = ""
    try:
        global sl
        sl = sl + 1
        if sl > max_sl:
            print("sleep ", sl)
            sleep_sec(1)
            sl = 0
        q_type = tkr.info['quoteType']
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
    current_price = _get_market_price_1(ticker_symbol)
    while current_price < 0:
        sleep_sec(3)
        current_price = _get_market_price_1(ticker_symbol)
    return current_price

def _get_market_price(ticker_symbol):
    # Download the most recent data (intraday data)
    current_price = 0
    try:
        tkr = yf.download(ticker_symbol, period="1d", interval="1m")
        found = True
    except:
        found = None
    finally:
        if found:
            if isinstance(tkr, DataFrame):
                if not tkr.empty:
                    pprint(type(tkr))
                    current_price = tkr['Close'].iloc[-1]
        # Access the current closing price (assuming you downloaded recent data)
        # You can access other data points like 'Open', 'High', 'Low', etc.
                    print(f"Current Price of {ticker_symbol}: {current_price}")

        return str(current_price)

if __name__ == "__main__":
    # sleep_sec(10)
    for i in [1,2,3,4,5,6,7,8,9,10]:

        for l in ['PLTU', 'ILTB', 'SNDK', 'SPHIX', 'OKTA', 'G637AM102', 'ARKK', 'AAPL', 'T']:
            print({l: get_market_price(l)})

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