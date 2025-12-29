
from base_lib.core.sys_utils import Today
# from TradeUtil import BaseTrade1, BaseObjectItem, BaseTradeSymbol
header_lines = 3
# rootdir = 'C:\\Users\\Consultant\\OneDrive\\Satyen\\family\\vepar\\'

rootdir = 'G:\\My Drive\\vepar\\'

order_file = rootdir+"all_orders.csv"
pos_file = rootdir+"all_positions.csv"
pos_file_new = rootdir+"all_positions_new.csv"
closed_pos_file = rootdir+"all_closed_positions.csv"
hist_file = rootdir+"all_history.csv"
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

if __name__ == '__main__':
    print(output_file)
    import os
    from os.path import isfile, join
    files = [f for f in os.listdir(rootdir) if isfile(join(rootdir, f))]
    for f in files:
        print(f)