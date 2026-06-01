import time
import random
from multiprocessing import Process, Manager, Lock

from tp.market.MrktDataUtil import getTickerObj

'''
            "sector" :  info.get('sector'),
            "book_value" :  info.get('bookValue'),
            "shares" :  info.get('sharesOutstanding'),
            "growth" :  info.get('earningsQuarterlyGrowth'),
            "quoteType" :  info.get('quoteType'),
            "current_price" :  info.get('currentPrice'),
            "PE" :  info.get('trailingPE'),
            "ForwardPE" :  info.get('forwardPE'),
            "DividendYield" :  info.get('dividendYield'),
            "ROE" :  info.get('returnOnEquity'), *100
            "PEG" :  info.get('pegRatio'),
            "ProfitMargin" :  info.get('profitMargins'),
            "RevenueGrowth" :  info.get('revenueGrowth'),
            "EarningsGrowth" :  info.get('earningsGrowth'),
            "MarketCap" :  info.get('marketCap'),
            "DebtToEquity" :  info.get('debtToEquity'),
            "high_quality = "_high_quality()
'''

critical_fields = ["price", "pe", "yield"]

def updater(shared_market_data, lock, tickers):
    while True:
        for ticker in tickers:
            info = getTickerObj(ticker)
            if not info:
                continue
            print("updating...", ticker)
            row = {}
            for cf in critical_fields:
                row[cf] = info.get(cf)

            #
            # # info = getTickerObj(ticker).info
            # row = {
            # # "sector" :  info.get('sector'),
            # # "book_value" :  info.get('bookValue'),
            # # "shares" :  info.get('sharesOutstanding'),
            # # "growth" :  info.get('earningsQuarterlyGrowth'),
            # # "quoteType" :  info.get('quoteType'),
            # # "current_price" :  info.get('currentPrice'),
            # # "PE" :  info.get('trailingPE'),
            # # "ForwardPE" :  info.get('forwardPE'),
            # # "DividendYield" :  info.get('dividendYield'),
            # # "ROE" :  info.get('returnOnEquity'),
            # # "PEG" :  info.get('pegRatio'),
            # # "ProfitMargin" :  info.get('profitMargins'),
            # # "RevenueGrowth" :  info.get('revenueGrowth'),
            # # "EarningsGrowth" :  info.get('earningsGrowth'),
            # # "MarketCap" :  info.get('marketCap'),
            # # "DebtToEquity" :  info.get('debtToEquity'),
            # #     "price": round(info., 2),
            #     "price": round(random.uniform(100, 300), 2),
            #     "pe": round(random.uniform(10, 40), 2),
            #     "yield": round(random.uniform(0, 5), 2),
            #     "updated_at": time.strftime("%H:%M:%S"),
            # }

            with lock:
                shared_market_data[ticker] = row

        time.sleep(1)



def get_ticker(shared_market_data, lock, ticker):
    with lock:
        data = shared_market_data.get(ticker)

    return data


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "KO"]

    with Manager() as manager:
        shared_market_data = manager.dict()
        lock = Lock()

        updater(shared_market_data, lock=lock, tickers=tickers)

        p_updater = Process(
            target=updater,
            args=(shared_market_data, lock, tickers),
            daemon=True
        )

        p_updater.start()

        # Main app reads only when needed
        time.sleep(1)

        print("AAPL:", get_ticker(shared_market_data, lock, "AAPL"))

        time.sleep(1)

        print("MSFT:", get_ticker(shared_market_data, lock, "MSFT"))

        p_updater.terminate()
        p_updater.join()