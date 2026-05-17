from pandas.core.frame import DataFrame
from get_price import getMarketCurrentAndHistory
from ta.momentum import RSIIndicator
RSI_WINDOW = 14


def calc_rsi_for_tkr(tkr_df):
    close_prices = tkr_df['Close']
    rsi = RSIIndicator(close_prices, window=RSI_WINDOW).rsi().iloc[-1]
    return rsi

def refresh_ticker_details(tkr_list: list, cd: dict, hd: DataFrame):
    for tkr in tkr_list:
        df = hd[tkr].dropna()
        if len(df) < RSI_WINDOW + 1:
            rsi = None
        rsi = calc_rsi_for_tkr(df)
        pass


if __name__ == "__main__":
    tkr_list = ['SPY', 'QQQ', 'IWM']
    cd, hd = getMarketCurrentAndHistory(tkr_list)
    refresh_ticker_details(tkr_list, cd, hd)
