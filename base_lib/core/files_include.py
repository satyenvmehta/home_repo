
from base_lib.core.sys_utils import Today
# from TradeUtil import BaseTrade1, BaseObjectItem, BaseTradeSymbol
header_lines = 3
# rootdir = 'C:\\Users\\Consultant\\OneDrive\\Satyen\\family\\vepar\\'

rootdir = 'G:\\My Drive\\vepar\\'

order_file = rootdir+"all_orders.csv"
pos_file = rootdir+"all_positions.csv"
pos_file_new = rootdir+"all_positions_new.csv"
closed_pos_file = rootdir+"all_closed_positions.csv"
hist_file = rootdir+"all_history.csv"   # all_history_dbg
int_scan_file = rootdir+"inteli_scan.csv"
ticker_file = rootdir+"ticker.csv"
stock_fundamentals_file = rootdir+"stock_fundamentals.csv"
sp_500_file = rootdir+"sp_500.xlsx"
nasd_100_file = rootdir+"nasd_100.xlsx"
my_symbol_xls_file = rootdir+"MySymbols.xlsx"
weekly_fundamentals_file = rootdir+"fundamentals_weekly.csv"
weekly_fundamentals_file_debug = rootdir+"fundamentals_weekly_debug.csv"

tday = Today('%b-%d')
output_file = rootdir+"output-" + tday + ".xlsx"
print(output_file)
alt_output_file = rootdir+"alt_output.xlsx"
# from base_classes import BaseObject
import pandas as pd

def prep_ticker_list():
    # Read both Excel files (assume first column contains tickers)
    df1 = pd.read_excel(sp_500_file)
    df2 = pd.read_excel(nasd_100_file)
    df3 = pd.read_csv(ticker_file)
    df_my = pd.read_excel(my_symbol_xls_file)

    # Combine tickers from both sheets, remove duplicates, drop NaN
    tickers = pd.concat([df1, df2, df3, df_my], ignore_index=True).iloc[:, 0].dropna().unique().tolist()
    # tickers = ['AAA', 'ABBV', 'MBLY', 'LMT', 'NGD', 'avxx', 'orcl', 'orcx', 'hmy']
    tickers = sorted(tickers)
    return tickers

if __name__ == '__main__':
    print(output_file)
    import os
    from os.path import isfile, join
    files = [f for f in os.listdir(rootdir) if isfile(join(rootdir, f))]
    for f in files:
        print(f)

    print(prep_ticker_list())