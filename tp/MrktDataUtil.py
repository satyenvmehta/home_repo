

from base_lib.core.base_classes import *

# # from base_classes import BaseObject, BaseObjectItem,  BaseString, BaseFloat, BaseMoney,  BaseCustomStatus, BasePercentage
# from base_lib.core.base_container_classes import    BaseReaderWriter,  BaseSet,  BaseList, BaseContainer, BaseDict, BaseBuySell
# from base_lib.core.common_include import MFList
from base_lib.core.files_include import stock_fundamentals_file, weekly_fundamentals_file_debug

from tp.market.get_price import getHistoricalData, getTickerInfo
from TradeUtil import _validate_ticker, prep_ticker_list, prep_debug_list
RefreshInterval = 7

import builtins
print = builtins.print

@dataclass
class MarketData(BaseObject):
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
        # self.tickers = prep_debug_list()
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


from ta.momentum import RSIIndicator
RSI_WINDOW = 14
def _get_rsi(df):
    # df = data[ticker].dropna()
    if len(df) < RSI_WINDOW + 1:
        return None
    rsi = RSIIndicator(df['Close'], window=RSI_WINDOW).rsi().iloc[-1]
    return rsi

if __name__ == '__main__':
    mrk_data = MarketData(debug=True)
    mrk_data.refreshWeeklyInfo(save_file=weekly_fundamentals_file_debug)
    for t in mrk_data.getTickers():
        rsi = mrk_data.getRSI(t)
        print(f"{t} RSI: {rsi}")
    mrk_data.getWeeklyInfo(save_file=stock_fundamentals_file)

