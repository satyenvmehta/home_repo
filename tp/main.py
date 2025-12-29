from datetime import datetime
import sys
# base_lib = r'G:\My Drive\Software\PycharmProjects\base_lib'
# sys.path.append(base_lib)




# from base_lib.core.base_include import *
# from tp.market.client_fe import MarketPrice

ExceptionTicker = [
'L4135L100','SPAXX','SRNEQ','TSPH', 'SCLX', 'SRNE', "FZDXX"
]

Debug_tickers = ['TQQQ' ]

# Adjust Prices for 2nd B or Sell Order prices
# Adjust_prices = []
def pending_items():
    print("===============Pending Items=================")
    # print("Use Business Date to find 5 days difference")
    print("Use Pre-Market Price if available")
    print("")
    # print("Filtered out Filled orders")

    print("CHECK REF PRICE IN ORDER TO PROVIDE ADJUST PRICE LOGIC - Missed UPST - Adjust Buy Price (16.01%)@24.91_S_26.25_-17.0 on Jun 11th")
    print("Accelaration of Gain/Loss to be considered for Sell/Buy Order")
    # print("Add asof Date in footer/Headerr")
    # print("Buy/Sell Qty in recommendation column")
    print("Summarize History with total no of B//S, G/L, Avg G/L, Avg Price, Avg Qty, Avg Cost")
    print("Think @ 5% daily deviation strategy")
    print("Add % of Gain/Loss in footer")
    print("Identify Idle Tkrs")
    print("Identify low value securities and reduce exposure")
    print("Identify G/L and % G/L based on history per ticker")
    print("Add Yield as param to hold for longer time/higher G/L")
    print("Create an Oppsite DAY Order with 5% diff - in addition to 10% GTC")
    print("File Save as AsOfDate")
    print("Sell Price uses - lastP as ref and NOT history - for ex: IQ - Sell@4.38_B_3.6_75.0 and LastP = 3.98")
    print("Create Pivot based on history giving picture of P/L and cost/share ")
    print("Rounding off to 2 decimal places")
    print("LastP - 182 for CEG	Buy@107.79_S_129.0_-3.0	SMMrkCap - need better logic for recommending")
    # print("COST	Adjust Buy Price (53.74%)@761.8_S_520.37_-1.0  doesnt make sense - current order is at 800")
    # print("Price_LastH_Price_Qty - append R_Qty for Sell orders")
    # print("Sell@181.65_B_185.0_1.0 - should have Sell@195 - not 181.65")
    print("==================================================")
    print("Repot competed on " + str(datetime.now().date()) + " " + str(datetime.now().time()) )
    return
import trade_processing
if __name__ == '__main__':

    # from set_path import append_lib_path
    # append_lib_path()
    # import math_utils
    # print(math_utils.hex2float('A'))

    # if 'SPAXX' in ExceptionTicker:
    #     raise Exception('SPAXX')

    trade_processing.tp()
    pending_items()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
