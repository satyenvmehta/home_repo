from datetime import timedelta

import pandas as pd
from pandas import DataFrame

from dateutil.utils import today

from tp.TradeUtil import BaseTrade, BaseTrades

threshold = 5

posThreshold = threshold
negThreshold = -threshold
import common_include as C
header_lines = 6
from tp_include import *

@C.dataclass
class History(BaseTrade):
    Symbol: C.BaseTradeSymbol = None
    Date: C.BaseDate = None
    Quantity: C.BaseFloat = None
    Price: C.BaseTradePrice = None
    Amount: C.BaseTradePrice = None
    Account:C.BaseString = None
    Description: C.BaseBuySell = None

    def getPrice(self):
        return self.Price.getBase()
    def getQuantity(self):
        return self.Quantity.getBase()

    # def isAnIdleSecurity(self):
    #     return self.Date.isOlderThan(45)

    def __str__(self):
        ps = str(self.Symbol) + "|" + str(self.Price)  + "|"+ str(self.Quantity)  + "|" + str(self.Description)
        return ps

    def isOlderThan(self, days=30):
        return self.Date.isOlderThan(days)

    def canBeSold(self):
        return self.isOlderThan()

    def isBuy(self):
        return self.getBuySell() == 'B'

    def isSell(self):
        return self.getBuySell() == 'S'

    def getBuySell(self):
        return self.Description.getBase()

    def matchesRefObj(self, bs):
        if bs == 'B':
            if self.isBuy():
                return self
        else:
            if self.isSell():
                return self
        return None

    @classmethod
    def from_dict(cls, data_dict):
        o =  cls(data_dict[Symbol],	data_dict['Date'], data_dict['Quantity'],
                   data_dict['Price'],	data_dict['Amount'],data_dict['Account'], data_dict['Description'])
        # o.noOfDaysSinceTrans()
        return o
from account import AccountManager

@C.dataclass
class Historys(BaseTrades):
    def __post_init__(self):
        self.summary_df = None
        super().__post_init__()
        sort_by = lambda x: x.Date
        self.presetTrades(sort_by=sort_by, reverse=True)
        self.cls = History
        self.uniqueCols = [	Symbol,	Amount,]
        self.readFile(self.cls, self.uniqueCols, header_lines=header_lines, datafile=C.hist_file)
        df = self.getDF()

        self.all_symbols = df[Symbol].unique()
        self.prep_summ_df()
        self._histSumm = C.BaseDict()
        # self.initHistorySummary()
        # self.idle_trade_qry(45)
        self.postDFProcess()
        return

    def getSummaryForSymbol(self, sym):
        if isinstance(sym, C.BaseObject):
            sym = sym.getBase()
        return self._histSumm.getValue(sym)

    # def getSummaryObjForSymbol(self, sym):
    #     if isinstance(sym, C.BaseObject):
    #         sym = sym.getBase()
    #     return self._histSumm.getSummaryObj(sym)

    def postDFProcess(self):
        self.updateDateFormat()
        self.updateDFDescriptionToBS()
        self.history_since()
        return

    def updateDFDescriptionToBS(self):
        df = self.getDF()
        if not isinstance(df, DataFrame):
            return
        df[Description] = df[Description].apply(lambda x: "B" if x == "YOU BOUGHT" else ("S" if x == "YOU SOLD" else x))
        return

    def updateDateFormat(self):
        df = self.getDF()
        if not isinstance(df, DataFrame):
            return
        df[Date] = pd.to_datetime(df[Date], format='%m/%d/%Y')
        # df[Date] = df[Date].apply(lambda x: x.replace("/", "-"))
        return

    def getRecordsForSym(self, sym):
        df = self.getDF()
        return df.loc[df[Symbol] == sym]
    def getRecordForAcct(self, acct):
        df = self.getDF()
        return df.loc[df[Account] == acct]

    def getRecordForAcctAndSym(self, acct, sym, bs='B'):
        df = self.getDF()
        return df.loc[(df[Account] == acct) & (df[Symbol] == sym) & (df[Description] == bs)]

    def getLastBoughtForAcctAndSym(self, acct, sym):
        df = self.getRecordForAcctAndSym(acct, sym,  bs='B')
        if df.empty:
            return None
        df = df.sort_values(by=[Date], ascending=False)
        return df.iloc[0]

    def boughtInLastNDays(self, acct, sym, days=30):
        df = self.getRecordForAcctAndSym(acct, sym, bs='B')
        if df.empty:
            return False
        df = df.sort_values(by=[Date], ascending=False)
        lastBought = df.iloc[0]
        if lastBought.Date > pd.Timestamp.now() - pd.Timedelta(days=days):
            return True
        return False

    def getActListToSell(self, sym, pos, no_of_days=30):
        # accts = self.boughtRecently(sym)
        accts = self.getHoldingAccounts()
        actSellList = C.BaseList()
        for act in accts.getBase():
            if not self.boughtInLastNDays(sym=sym, acct=act):
                if pos.getCurrentObj(sym,  act):
                    actSellList.append(act)

        am = AccountManager()
        aidList = am.actListToActIdList(actSellList.getBase())
        return actSellList,  aidList

    def ifTradedRecently(self, sym,  bs=None):
        hobj = self._getRefObjForSymbol(sym, bs)
        if hobj:
            if hobj.canBeSold():
                return False,  None
        else:
            return False, None
        return True,  hobj
    def boughtRecentlyForAct(self, sym, act, no_of_days=30):
        hobj = self.getLastBoughtForAcctAndSym(sym=sym, acct=act)
        if hobj is None:
            return False
        return True

    def boughtRecently(self, sym, no_of_days=30):
        accts = self.getHoldingAccounts()
        actBuyList = C.BaseList()
        for act in accts.getBase():
            if self.boughtRecentlyForAct(sym, no_of_days=no_of_days,  act=act):
                actBuyList.append(act)
        return actBuyList

    def canSell(self, sym, no_of_days=30):
        if self.boughtRecently(sym, no_of_days=no_of_days):
            return False
        return True

    def idle_trade_qry(self, no_of_days=90):
        df = self.getDF()
        DateCol = 'datepd'
        df[DateCol] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

        # Define the date range (last six months from today)
        end_date = C.datetime.now()
        start_date = end_date - timedelta(days=no_of_days)

        recent_traded = df[(df[DateCol] >= start_date) & (df[DateCol] <= end_date)]
        active_symbols = recent_traded[Symbol].unique()
        self.idle_symbols = list(set(self.all_symbols) - set(active_symbols))
        return self.idle_symbols

    def history_since(self, sdate="09/15/2024"):
        self.buy_bucket = C.BaseSet()
        self.sell_bucket = C.BaseSet()
        for item in self.getBase():
            if isinstance(item, History):
                if (item.Date > sdate):
                    if item.isBuy():
                        self.buy_bucket.append(item.Symbol.getBase())
                    else:
                        self.sell_bucket.append(item.Symbol.getBase())
        return

    def list_approved_since(self):
        # return
        self.sell_bucket.print()
        self.buy_bucket.print()
        return

    def isApproved2Buy(self, sym):
        return self.buy_bucket._exists(sym)
    def isApproved2Sell(self, sym):
        return self.sell_bucket._exists(sym)

    # def getLastQuantity(self, sym):
    #     qty = self.summary_df.loc[self.summary_df[Symbol] == sym, 'last_qty'].iloc[0]
    #     return abs(qty)

    def hasHistory(self, sym):
        if sym in self.summary_df[Symbol].values:
            return True
        return False

    def getHistoryPrice(self, sym):
        if self.hasHistory(sym):
            return self.summary_df.loc[self.summary_df[Symbol] == sym, 'last_price'].iloc[0]
        return None

    def getLastPrice(self, sym):
        return self.getFloatValueForSymbol(sym, 'last_trade_price')
    def getLastQuantity(self, sym):
        val = self.getSummaryAttrForSymbolFromDF(sym, 'last_trade_qty')
        if not val:
            return 0
        return round(float(val), 2)

    def getLastTradeDate(self, sym):
        return self.getSummaryAttrForSymbolFromDF(sym, last_trade_date).strftime('%Y-%m-%d')

    # def _isAnIdleSecurity(self, sym, days_since_last=30):
    #     print("Invalid call for isAnIdleSecurity")
    #     self.idle_symbols = None
    #     return None
    #     last_trd_date = self.getLastTradeDate(sym)
    #     if last_trd_date is None:
    #         return True
    #     if last_trd_date.isOlderThan(days_since_last):
    #         return True
    #     return sym in self.idle_symbols

    def getSummaryAttrForSymbolFromDF(self, sym, attr):
        df = self.getSummary()
        try:
            val = df.loc[self.summary_df[Symbol] == sym, attr].iloc[0]
        except Exception as e:
            if isinstance(sym, C.BaseObject):
                sym = sym.getBase()
            # print(f"getSummaryAttrForSymbolFromDF: ATTR : {attr} FOR SYMBOL : {sym} not found in summary_df")
            return None
        return val

    def prep_summ_df(self):
        if self.summary_df:
            return self.summary_df
        history_trades_df = self.getDF()
        # history_trades_df[Price].replace({'\,': ''})
        history_trades_df['price'] = history_trades_df[Price].replace({'\$': ''}, regex=True).replace({',': ''}, regex=True).astype(float)
        history_trades_df['quantity'] = history_trades_df[Quantity].replace({',': ''}, regex=True).astype(float)

        # Convert 'trade_date' to datetime for any date-based operations
        history_trades_df['trade_date'] = pd.to_datetime(history_trades_df[Date])
        history_trades_df = history_trades_df.sort_values('trade_date', ascending=False)
        # self.trade_count = len(history_trades_df)

        # Group by 'symbol' and aggregate data
        self.summary_df = history_trades_df.groupby(Symbol).agg(
            last_trade_type = ('quantity', lambda x: 'Buy' if x.iloc[0] > 0 else 'Sell'),
            last_date=('trade_date', lambda x: x.max().date()),  # Last trade date
            last_trade_price=('price', 'first'),
            ltp_less_5_pct=('price', lambda x: round(x.iloc[0] * 0.95, 2)),
            ltp_more_5_pct=('price', lambda x: round(x.iloc[0] * 1.05, 2)),
            last_trade_qty=('quantity', 'first'),
            qty_buy=('quantity', lambda x: x[x > 0].sum()),  # Sum of positive quantities for buy trades
            qty_sell=('quantity', lambda x: x[x < 0].sum()),  # Sum of negative quantities for sell trades
            avg_buy_price=('price', lambda x: round(x[history_trades_df.loc[x.index, 'quantity'] > 0].mean(), 2)),
            avg_sell_price=('price', lambda x: round(x[history_trades_df.loc[x.index, 'quantity'] < 0].mean(), 2)),
            isAnIdleSymbol=('trade_date', lambda x: (C.datetime.date(today()) - x.max().date() > timedelta(days=IdleSecurityDays))),
            first_trade_price=('price', 'last'),  # Last trade price

            # if_last_trade_buy=('price', lambda x: True if x[history_trades_df.loc[x.index, ('quantity', 'first')] > 0]else False),
            # if_first_trade_buy=('price', lambda x: True if x[history_trades_df.loc[x.index, ('quantity', 'last')] > 0] else False),
            total_buy_amt=('price', lambda x: round(x[history_trades_df.loc[x.index, 'quantity'] > 0].sum(), 2)),
            # # Total buy amount
            total_sell_amt=('price', lambda x: round(x[history_trades_df.loc[x.index, 'quantity'] < 0].sum(), 2)),
            # Average sell price
            trade_count=(Quantity, 'count'),  # Count of trades
            first_date=('trade_date', lambda x: x.min().date())  # First trade date
            , days_since_last=('trade_date', lambda x: (pd.Timestamp.now() - x.max()).days)
            , bus_days_since_last=('trade_date', lambda x: C.getNoOfBusinessDaysFromDate(x.max()))
            , days_since_first=('trade_date', lambda x: (pd.Timestamp.now() - x.min()).days)
        ).reset_index()

        # Calculate the gain/loss (considering negative quantity for sell)
        self.summary_df['gain_loss'] = (self.summary_df['avg_sell_price'] - self.summary_df['avg_buy_price']) * abs(
            self.summary_df['qty_sell'])
        self.summary_df['gain_loss'] = self.summary_df['gain_loss'].apply(lambda x: round(x, 2))
        return self.summary_df

    def symHasHistory(self, sym):
        if sym in self.summary_df[Symbol].values:
            return True
        return False
    def getLastTradeType(self, sym):
        return self.getSummaryAttrForSymbolFromDF(sym, 'last_trade_type')
    def getLastAction(self, sym):
        ltt = self.getLastTradeType(sym)
        if ltt:
            return ltt[0]
        return None
    def isAnIdleSymbol(self, sym):
        return self.getSummaryAttrForSymbolFromDF(sym, 'isAnIdleSymbol')
    def getNoOfDaysSinceLastTrade(self, sym):
        return int(self.getSummaryAttrForSymbolFromDF(sym, 'days_since_last'))
    def getNoOfBusDaysSinceLastTrade(self, sym):
        return int(self.getSummaryAttrForSymbolFromDF(sym, 'bus_days_since_last'))
    # def getLastTradeDate(self, sym):
    #     return self.getSummaryAttrForSymbolFromDF(sym, last_trade_date)
    def getNoOfDaysSinceFirstTrade(self, sym):
        return int(self.getSummaryAttrForSymbolFromDF(sym, 'days_since_first'))

    def if_last_trade_buy(self, sym):
        if self.getLastTradeType(sym) == 'Buy':
            return True
        return False

    def if_first_trade_buy(self, sym):
        if not self.getSummaryForSymbol(sym):
            return None
        return self.getSummaryForSymbol(sym).if_first_trade_buy

    def getSymbolsWithLastTradedDate(self):
        # self.summary_df['last_trade_date'] = pd.to_datetime(self.summary_df['last_trade_date'])
        self.summary_df = self.summary_df.sort_values(by=last_trade_date, ascending=False)
        return self.summary_df

    def getFloatValue(self, val):
        return float(val.replace('$', '').replace(',', ''))
    def getIntValue(self, val):
        return int(val.replace('$', '').replace(', ', ''))

    def getSummary(self):
        return self.summary_df
    def getAllSymbols(self):
        return self.all_symbols

    def getFloatValueForSymbol(self, sym,  attr):
        if isinstance(sym, C.BaseObject):
            sym = sym.getBase()
        value = self.getSummaryAttrForSymbolFromDF(sym, attr)
        if not value:
            return 0.0
        return float("{:.2f}".format(value))
    def getIntValueForSymbol(self, sym,  attr):
        if isinstance(sym, C.BaseObject):
            sym = sym.getBase()
        value = self.getSummaryAttrForSymbolFromDF(sym, attr)
        return int(value)

    def lastTradeQty(self, sym):
        return self.getFloatValueForSymbol(sym, 'last_trade_qty')
    def getGainLossForSymbol(self, sym):
        return self.getFloatValueForSymbol(sym, 'gain_loss')

def Dbg_DF():
    data = {
        'symbol': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL', 'MSFT', 'MSFT', 'TSLA', 'TSLA'],
        'date': ['2023-01-01', '2023-06-01', '2023-01-01', '2022-11-01', '2023-01-01', '2022-10-01', '2023-01-01',
                 '2022-08-01'],
    }

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

def print_history(hist):
    df = Dbg_DF()
    if isinstance(hist, Historys):
        listOfInterest = { 'History': hist,
                          'HistorySummary': hist.summary_df}
        hist._saveResults(listOfInterest=listOfInterest, fileName=C.alt_output_file, altFilename=C.alt_output_file)
    return

if __name__ == '__main__':
    ht = Historys()
    print(ht.isAnIdleSymbol('MS'))

    print_history(ht)
    for sym in ht.getAllSymbols():
        if ht.isAnIdleSymbol(sym):
            print(f"{sym} is an idle symbol")
            continue
        print(sym)
        print(ht.getNoOfDaysSinceLastTrade(sym))
        print(ht.getNoOfBusDaysSinceLastTrade(sym))
        print(ht.getNoOfDaysSinceFirstTrade(sym))
        print(ht.if_last_trade_buy(sym))
        print(ht.getSummaryAttrForSymbolFromDF(sym, 'qty_buy'))
        print(ht.getLastQuantity(sym) *1.1)
        price = ht.getLastPrice(sym)
        print({sym: price})
        last_trade_type = ht.getSummaryAttrForSymbolFromDF(sym, 'last_trade_type')
        qty, bs, gnl = ht.lastTradeQty(sym), last_trade_type,  ht.getGainLossForSymbol(sym)
        print({"qty": qty, "bs": bs,  "gnl": gnl})
        f_buy, l_buy = ht.getFloatValueForSymbol(sym, 'avg_buy_price'), ht.getFloatValueForSymbol(sym, 'avg_sell_price')

        print({"f_buy": f_buy, "l_buy": l_buy, "last_trade_type": last_trade_type})
        print(ht.isApproved2Buy(sym))
        print(ht.isApproved2Sell(sym))
        print(ht.getGainLossForSymbol(sym))
    x = 2.2222
    y2 = float("{:.2f}".format(x))
    from position import Positions
    p = Positions()
    syn = 'UPST'
    print(ht.boughtRecently(syn))
    for syn in ht.getAllSymbols():
        x, aids = ht.getActListToSell(syn, p)
        print(syn)
        if x.isEmpty():
            continue
        print( aids)
        actList = ht.boughtRecently(syn)
        # for acct in actList.getBase():
        #     print(acct)
        #     if ht.ifBoughtInLastNDays(acct.getBase(),  syn):
        #         print("Bought in last 30 days")
        #     else:
        #         print("Not bought in last 30 days")


        # print(ht.canSell(sym))
    # syn = 'UPST'
    # ht.resetForNextSym(syn)
    # lst = ht.getRefObjsForSymbol(syn)
    # ht.getSymbolsWithLastTradedDate()

    # print(ht.getNextBuyRefPrice())
    ht.idle_trade_qry()


