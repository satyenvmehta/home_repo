from datetime import datetime

import pandas as pd
from base_lib.core.base_classes import BasePrice
from ta.momentum import RSIIndicator

from MrktDataUtil import  MarketData #() ignore_ticker, prep_ticker_list, prep_debug_list



from position import Positions
from sc_util import StockFilterAttributes
from tp.order import Orders

RSI_WINDOW = 14
RSI_OVERBOUGHT = 69
RSI_OVERBOUGHT_PLUS = 79
RSI_OVERSOLD = 32
RSI_OVERSOLD_MINUS = 22

IntraDayKey = "Intraday %"
# Ticker	last	BS?	Pos	Intraday %	OC_gap%	ONight Gap%	High	Low	RSI	BS_IND	Pos
interested_fields = ["Ticker",  "last", "High", "Low", "BS_?", "Pos", IntraDayKey, "OC_gap %", "ONight Gap %",  "RSI", "BS_IND"] #, "Pos"]

positions = Positions()
orders = Orders()

def getRSI(df, window=RSI_WINDOW):
    delta = df["Close"].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    average_gain = up.rolling(window).mean()
    average_loss = down.rolling(window).mean()
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_orders_exists(ticker):
    be = orders.exists(ticker, "Buy")
    se = orders.exists(ticker, "Sell")
    if be and se:
        return True, True
    if be:
        return True, False
    if se:
        return False, True
    return False, False
def get_rsi(data, ticker):
    df = data[ticker].dropna()
    if len(df) < RSI_WINDOW + 1:
        return None, None, None

    be, se = get_orders_exists(ticker)

    rsi = RSIIndicator(df['Close'], window=RSI_WINDOW).rsi().iloc[-1]
    if rsi > RSI_OVERBOUGHT_PLUS:
        bs_indicator = "Overbought+"
        bd_advise = "StrongSell"
    elif rsi > RSI_OVERBOUGHT:
        bs_indicator = "Overbought"
        bd_advise = "Sell"
    elif rsi < RSI_OVERSOLD_MINUS:
        bs_indicator = "Oversold-"
        bd_advise = "StrongBuy"
    elif rsi < RSI_OVERSOLD:
        bs_indicator = "Oversold"
        bd_advise = "Buy"
    else:
        bs_indicator = "Neutral"
        bd_advise = "Hold"
    PLUS = "+"
    if bd_advise.endswith("Buy"):
        if be:
            bd_advise = bd_advise + PLUS
    if bd_advise.endswith("Sell"):
        if se:
            bd_advise = bd_advise + PLUS

    return BasePrice(rsi), bs_indicator, bd_advise

def append_filter_to_result(sfa, result):
    if isinstance(result, list):
        result.append(
            [sfa.Symbol.getBase()
                , sfa.close_today.getBase()
                , sfa.today_high.getBase()
                , sfa.today_low.getBase()
                , sfa.bd_advise
                , sfa.pos
                , sfa.intraday_range_per.getBase()
                , sfa.open_close_gap_per.getBase()
                , sfa.overnight_gap.getBase()
                , sfa.rsi.getBase()
                , sfa.bs_indicator
             ])


def find_stocks_multi():
    # Get all tickers at once
    mrk_data = MarketData(debug=False)
    tickers = mrk_data.getTickers()
    data = mrk_data.getHistoricalData()

    results = []
    other_results = []
    rest_results = []

    sfa = StockFilterAttributes()

    for ticker in tickers:
        try:
            df = data[ticker].dropna().tail(2)
            if len(df) < 2:
                continue
            rsi, bs_indicator, bd_advise = get_rsi(data, ticker)
            pos = positions.getTotalQty(ticker)
            if pos == 0 or pos is None:
                if bd_advise.endswith("Sell"):
                    bd_advise = "NA"

            sfa.init_from_df(ticker, df, rsi, bs_indicator, bd_advise, pos)
            open_close_gap_abs = abs(sfa.open_close_gap_per.getBase())
            if sfa.intraday_range_per.getBase() > 3.5:
                if open_close_gap_abs < 1.5:
                    append_filter_to_result(sfa, results)
                else:
                    if sfa.intraday_range_per.getBase() > 5.0:
                        append_filter_to_result(sfa, other_results)
                    else:
                        append_filter_to_result(sfa, rest_results)
            else:
                append_filter_to_result(sfa, rest_results)

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    r_15 = pd.DataFrame(results, columns=interested_fields)
    r_more_15 = pd.DataFrame(other_results, columns=interested_fields)
    r_rest = pd.DataFrame(rest_results, columns=interested_fields)
    r_15 = r_15.sort_values(by=IntraDayKey, ascending=False)
    r_more_15 = r_more_15.sort_values(by=IntraDayKey, ascending=False)
    r_rest = r_rest.sort_values(by=IntraDayKey, ascending=False)
    return r_15,  r_more_15, r_rest
AllRecs = "All"
OC_LT_15 = "open_close_LT_1.5"
OC_GT_15 = "open_close_GT_1.5"
Rest = "rest"
SheetNames = [AllRecs, OC_LT_15, OC_GT_15, Rest]
if __name__ == "__main__":
    d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(d)
    print("started")
# ✅ Example list
#     tickers = ["AAPL", "TSLA", "AMD", "PLTR", "NVDA", "MARA", "SOFI", "BABA", "F", "TQQQ"]
#     tickers = prep_ticker_list()
    # tickers = prep_debug_list()
    df_15, df_more_15, df_rest = find_stocks_multi()
    print(df_15)
    print(df_more_15)
    print(df_rest)
    filen =  "G:\My Drive\\vepar\\stock_screener_" + datetime.now().strftime("%Y-%m-%d") + ".xlsx"
    sheet_name = datetime.now().strftime("%b_%d")  # e.g., "Aug_09"

    with pd.ExcelWriter(filen, engine="xlsxwriter") as writer:
        All = pd.concat([df_15, df_more_15, df_rest], ignore_index=True).sort_values(by="RSI", ascending=False)
        All.to_excel(writer, sheet_name=AllRecs, index=False)
        df_15.to_excel(writer, sheet_name=OC_LT_15, index=False)
        df_more_15.to_excel(writer, sheet_name=OC_GT_15, index=False)
        df_rest.to_excel(writer, sheet_name=Rest, index=False)

        workbook = writer.book
        ws_all = writer.sheets[AllRecs]
        ws_lt_15 = writer.sheets[OC_LT_15]
        ws_gt_15 = writer.sheets[OC_GT_15]
        ws_rest = writer.sheets[Rest]

        for name, worksheet in writer.sheets.items():
            worksheet.conditional_format('J2:J1000', {'type': 'cell',
                                                'criteria': 'greater than',
                                                'value': RSI_OVERBOUGHT,
                                                'format': workbook.add_format({'bg_color': '#C6EFCE',
                                                                               'font_color': '#006100'})})
            worksheet.conditional_format('J2:J1000', {'type': 'cell',
                                                'criteria': 'less than',
                                                'value': RSI_OVERSOLD,
                                                'format': workbook.add_format({'bg_color': '#FFC7CE',
                                                                               'font_color': '#9C0006'})})




    # df_15.to_excel(filen, sheet_name=sheet_name, index=0)
    # df_more_15.to_excel(filen, sheet_name=sheet_name + "_more_15", index=1)
    print("saved to ", filen)
