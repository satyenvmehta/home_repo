
import pandas as pd

import common_include as C
from ta.momentum import RSIIndicator

from MrktDataUtil import  MarketData #() ignore_ticker, prep_ticker_list, prep_debug_list

from position import Positions
from sc_util import StockFilterAttributes
from tp.all_history import Historys
# from tp.excel_support import ExcelCreator, FillColor, ConditionOp, Condition
from tp.order import Orders

RSI_WINDOW = 14
RSI_OVERBOUGHT = 69
RSI_OVERBOUGHT_PLUS = 79
RSI_OVERSOLD = 32
RSI_OVERSOLD_MINUS = 22

IntraDayKey = "Intraday %"
# Ticker	last	BS?	Pos	Intraday %	OC_gap%	ONight Gap%	High	Low	RSI	BS_IND	Pos
interested_fields = ["Ticker",  "last", "High", "Low", "BS_?", "Pos", IntraDayKey, "OC_gap %", "ONight Gap %",  "RSI", "BS_IND"] #, "Pos"]

# def init_stock_screener():
positions = Positions()
orders = Orders()
historys = Historys()
    # return positions, orders, historys

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

IGNORE = "_Ign"
def check_recent_history_price(ticker, bs, last):
    recent_price =  historys.recent_price(ticker, bs)
    ext_str = ""
    if not recent_price:
        return ext_str
    if bs.endswith('Buy'):
        if last > recent_price:
            return IGNORE
    if bs.endswith("Sell"):
        if last < recent_price:
            return IGNORE

    diff = abs(last - recent_price)
    diff_percen = diff / recent_price * 100
    if diff_percen <  4.0:
        ext_str = IGNORE
    return ext_str

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

    close_price = float(df['Close'].iloc[-1])

    price_ind = check_recent_history_price(ticker=ticker, bs=bd_advise, last=close_price)
    if price_ind == IGNORE:
        bd_advise = bd_advise + price_ind

    PLUS = "+"
    if bd_advise.endswith("Buy"):
        if be:
            bd_advise = bd_advise + PLUS
    if bd_advise.endswith("Sell"):
        if se:
            bd_advise = bd_advise + PLUS


    return C.BasePrice(rsi), bs_indicator, bd_advise

def append_filter_to_result(sfa, result):
    if isinstance(result, list):
        if sfa.rsi:
            rsival = sfa.rsi.getBase()
        else:
            rsival = None
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
                , rsival
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
    error_tickers = ['avxx', 'bmnz', 'hmy', 'orcl', 'orcx']
    tickers = error_tickers

    for ticker in tickers:
        try:
            ticker = ticker.upper()
            # if ticker in C.ignore_ticker:
            #     continue
            df = data[ticker].dropna().tail(2)
            if len(df) < 2:
                continue
            rsi, bs_indicator, bd_advise = get_rsi(data, ticker)
            pos = positions.getTotalQty(ticker)
            if pos == 0 or pos is None:
                if not bd_advise:
                    bd_advise = "NA"
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


def date_now(fmt):
    return C.datetime.now().strftime(fmt)

def fill_row_for_df(self, sheet, row: int, df, color):
    last_col = df.shape[1]
    rng = f"A{row}:{col_letter(last_col)}{row}"
    self.fill_range(sheet, rng, color)

def xlswriter_formatter(sheet, workbook, df, sheet_name):
    max_cols = df.shape[1]
    max_rows = df.shape[0]
    J_range = f'J2:J{max_rows}'
    fill_row_for_df(sheet_name, 1, df, FillColor.YELLOW)
    sheet.conditional_format(J_range, {'type': 'cell',
                                                'criteria': 'greater than',
                                                'value': RSI_OVERBOUGHT,
                                                'format': workbook.add_format({'bg_color': '#C6EFCE',
                                                                               'font_color': '#006100'})})
    sheet.conditional_format(J_range, {'type': 'cell',
                                                'criteria': 'less than',
                                                'value': RSI_OVERSOLD,
                                                'format': workbook.add_format({'bg_color': '#FFC7CE',
                                                                               'font_color': '#9C0006'})})

def apply_formatter(excel, df, sheet_name):
    # excel.fill_row_for_df(sheet_name, 1, df, FillColor.YELLOW)
    excel.conditional_format(
        sheet_name,
        "B2:B10",
        C.Condition(C.ConditionOp.GT, 50, C.FillColor.RED)
    )
if __name__ == "__main__":
    d = date_now("%Y-%m-%d %H:%M")
    print(d)
    print("started")
    df_15, df_more_15, df_rest = find_stocks_multi()
    All_data_df = pd.concat([df_15, df_more_15, df_rest], ignore_index=True).sort_values(by="RSI", ascending=False)
    print(df_15)
    print(df_more_15)
    print(df_rest)
    filen =  "G:\My Drive\\vepar\\stock_screener_" + date_now("%Y-%m-%d") + ".xlsx"
    # filen_2 = filen.replace(".xlsx", "_2.xlsx")
    sheet_name = date_now("%b_%d")  # e.g., "Aug_09"

    df_list = [All_data_df, df_15, df_more_15, df_rest]
    SheetNames = [AllRecs, OC_LT_15, OC_GT_15, Rest]
    df_dict = {SheetNames[i]: df_list[i] for i in range(len(SheetNames))}
    C.create_excel(filen, df_dict, apply_formatter)
    print("Done")

