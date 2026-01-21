from base_lib.core.files_include import ticker_file, sp_500_file, nasd_100_file, my_symbol_xls_file

import common_include as C
from tp.lib.tp_classes import BaseTradeSymbol, BaseTradePrice, BaseCustomStatus, BaseBuySell
from tp.market.get_price import  getTickerInfo

import pandas as pd

def get_my_symbols_df():
    return pd.read_excel(my_symbol_xls_file)

def prep_ticker_list():
    # Read both Excel files (assume first column contains tickers)
    df1 = pd.read_excel(sp_500_file)
    df2 = pd.read_excel(nasd_100_file)
    df3 = pd.read_csv(ticker_file)
    df_my = get_my_symbols_df()

    # Combine tickers from both sheets, remove duplicates, drop NaN
    tickers = pd.concat([df1, df2, df3, df_my], ignore_index=True).iloc[:, 0].dropna().unique().tolist()
    tickers = sorted(tickers)
    return tickers
def prep_debug_list():
    df_my = get_my_symbols_df()
    tickers = df_my.iloc[:, 0].dropna().unique().tolist()
    tickers = sorted(tickers)
    return tickers


@C.dataclass
class BaseTrade(C.BaseObject):
    Symbol: BaseTradeSymbol = None
    # Last: BaseTradePrice = None
    # Status: BaseCustomStatus = None

    def __str__(self):
        sym = str(self.Symbol) #+ " " + str(self.Status)
        # print(sym)
        return sym

    def getBuySell(self):   # Needs to be overriden by Derived class
        return None

    def __eq__(self, other):
        if isinstance(other, BaseTrade):
            res = self.Symbol == other.Symbol
        else:
            res = False
        return res

    def isPennyStock(self):
        return self.Last.getBase() < 2.0

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['Symbol']) #, data_dict['Status'])

    def to_dict(self):
        """ Return all attributes of the object as a dictionary """
        return vars(self)  # or self.__dict__

Symbol = 'Symbol'
@C.dataclass  #
class BaseTrades(C.BaseReaderWriter):
    def __post_init__(self):
        super(BaseTrades, self).__post_init__()
        sort_by = lambda x: x.Symbol
        self.presetTrades(sort_by=sort_by)
        self.all_symbols = None
        self.acctSet = None
        self.init_nones()
        return

    def post_read(self):
        for item in self.getBase():
            if isinstance(item, self.cls):
                # item.setDescDetails()
                if self.getDebug():
                    print(str(item))
            else:
                print("Cant customize")
        return

    def _read(self, header_lines, datafile):
        super().read( header_lines, datafile)
        self.post_read()
        return self.getBase()

    def getSymbolsWithLastTradedDate(self):
        # Group data by symbol and find the last date with a non-null closing price
        last_traded = self.getBase().groupby('Symbol')['Date'].last()
        return last_traded

    def setUnitClass(self, cls):
        self.cls = cls
        self.setClassMembersByTypes(cls)
        return

    def readFile(self, cls, uniqCols, header_lines, datafile):
        self.setUnitClass(cls)
        self.uniqueCols = uniqCols
        self._read(header_lines, datafile)  # Results in self.getBase()
        # for d in self.cls.
        return

    def getSelf(self):
        return self

    def saveToFile(self, fname):
        listOfInterest = {'Orders': self.getSelf()}
        super(BaseTrades, self)._saveResults(listOfInterest, fname)
        return

    def presetTrades(self, sort_by=None, reverse=False):
        self.resetDebug()
        self.sort_by = sort_by
        self.reverse = reverse
        return

    def getSortBy(self):
        return self.sort_by

    def sort_data(self, key, reverse):
        sdata = self.sort(self.getBase(), key=key, reverse=reverse)
        self.setBase(sdata)
        return sdata

    def postReadProcess(self):
        del_list = []
        for item in self.getBase():
            if isinstance(item, BaseTrade):
                if item.Symbol.isMF():
                    del_list.append(item)
        for ditem in del_list:
            self.remove(ditem)
            print("Removed " + ditem.Symbol.getBase())
            # self.getBase().  .remove(item, key="Symbol")
        return

    def _getUniqueSymbols(self):
        return self.getUniqueValuesForCol('Symbol')

    def getUniqueSymbols(self):
        return self.all_symbols

    def read(self, header_lines, data_file):
        super().read( header_lines, data_file)  # Get DF formated data
        self.postReadProcess()
        if self.getSortBy():
            self.sort_data(key=self.getSortBy(), reverse=self.reverse)
            # print("sorted data " + str(self.getSortBy()))
        return self.getBase()

    def getHoldingAccounts(self):
        if self.acctSet:
            return self.acctSet

        self.acctSet = C.BaseSet()
        for rec in self.getBase():
            if isinstance(rec, self.cls):
                if rec.Account.isNaN():
                    continue
                self.acctSet.append(rec.Account.getBase())
        return self.acctSet

    def printAccounts(self):
        if isinstance(self.acctSet, BaseSet):
            self.acctSet.print()
        return

    def getRecordsForSym(self, sym):
        filt_pos = C.BaseList()
        for pos in self.getBase():
            if isinstance(pos, self.cls):
                if pos.Symbol.equals(sym):
                    filt_pos.append(pos)
        return filt_pos

    def getFirstForSym(self, sym):
        ords = self.findSymbol(sym)
        if not ords:
            return None
        return ords.getFirst()

    def getCurrentObj(self, sym, acct=None):
        objs = self.findSymbol(sym)
        if not objs:
            return None
        if objs.isEmpty():
            return None
        if not acct:
            return objs
        if isinstance(acct, C.BaseObject):
            acct = acct.getBase()
        # foundObj = None
        foundObj = objs.getFirst()
        if objs.size() == 1:
            if acct:
                if foundObj.Account.getBase() == acct:
                    return foundObj
                else:
                    return None
            return foundObj

        for obj in objs.getBase():
            if isinstance(obj, self.cls):
                if obj.Account.getBase() == acct:
                    bestMatch = obj
                    return bestMatch
        return None

    def existsForSym(self, sym):
        objs = self.findSymbol(sym)
        if not objs:
            return False
        return True

    def findSymbol(self, sym, bs=None):
        if bs:
            if (bs == "Buy"):
                bs = "B"
            if (bs == "Sell"):
                bs = "S"

        results = C.BaseList()
        if not self.getBase():
            return None
        if isinstance(sym, C.BaseObject):
            sym = sym.getBase()
        for item in self.getBase():
            if isinstance(item, BaseTrade):
                if item.Symbol.getBase() == sym:
                    if not bs:
                        results.append(item)
                    else:
                        if isinstance(bs, BaseBuySell):
                            bs = bs.getBase()
                        if bs == item.getBuySell():
                            results.append(item)
        if results.isEmpty():
            return None
        return results

    def to_df(self):
        """ Convert the container of trades into a pandas DataFrame """
        data = [trade.to_dict() for trade in self.getBase()]
        res_df = pd.DataFrame(data)
        return res_df
        # return pd.DataFrame(data)
@C.dataclass
class OrderSampleClass(BaseTrade):
    Symbol : BaseTradeSymbol = None
    Last : BaseTradePrice = None
    Description : C.BaseString= None   # Buy 35 Limit at $26.25
    Status : BaseCustomStatus= None
    Account : C.BaseString= None
    def __post_init__(self):
        return

    # def getBuySell(self):
    #     return "B"

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['Symbol'], data_dict['Last'], data_dict['Description'], data_dict['Status'], data_dict['Account'])


@C.dataclass
class OrdersSampleClass(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        return

    def getLastPrice(self, sym):
        ord = self.getFirstForSym(sym)
        if isinstance(ord, self.cls):
            return ord.Last
        return None

def orderFileTesting():
    b = OrdersSampleClass()
    cls = OrderSampleClass
    uniqueCols = ['Symbol', 'Last', 'Trade Description', 'Status', ]
    header_lines = 3
    from base_lib.core.files_include import order_file
    b.readFile(cls, uniqueCols, header_lines, order_file)
    print(b.findSymbol('XBI', bs='B'))
    print(b.findSymbol('XBI'))
    row2Examin = 16
    b.examinRow(row2Examin)
    b.saveToFile("TestSample.xlsx")
    acc = b.getHoldingAccounts()

    df =  b.to_df()
    print(df)
    return


def getBestPrice(symbol):
    price = positions.getLastPrice(symbol)
    if price is not None:
        return price
    info = getTickerInfo(symbol)
    price = info.get('regularMarketPrice')
    if price is None:
        price = info.get('currentPrice')
    return price

@C.dataclass
class BuySellSet(C.BaseSet):
    def _multiEntries(self, obj):
        if not self.has(obj):
            return False
        return super().getCounts(obj) > 0

    def multiBuyCounts(self):
        return self._multiEntries('B')

    def multiSellCounts(self):
        return self._multiEntries('S')

    def isBuyOnly(self):
        return self.hasOnly('B')

    def isSellOnly(self):
        return self.hasOnly('S')

    def isBuyAndSellSet(self):
        return self.has(['B', 'S'])

if __name__ == '__main__':
    orderFileTesting()

