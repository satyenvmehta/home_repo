import common_include as C
import pandas as pd

@C.dataclass
class BaseTrade(C.BaseObject):
    Symbol: C.BaseTradeSymbol = None

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
            if not item:
                continue
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
        if isinstance(self.acctSet, C.BaseSet):
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
                        if isinstance(bs, C.BaseBuySell):
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
    Symbol : C.BaseTradeSymbol = None
    Last : C.BaseTradePrice = None
    Description : C.BaseString= None   # Buy 35 Limit at $26.25
    Status : C.BaseCustomStatus= None
    Account : C.BaseString= None
    def __post_init__(self):
        return

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
    b.readFile(cls, uniqueCols, header_lines, C.order_file)
    print(b.findSymbol('XBI', bs='B'))
    print(b.findSymbol('XBI'))
    row2Examin = 16
    b.examinRow(row2Examin)
    b.saveToFile("TestSample.xlsx")
    acc = b.getHoldingAccounts()

    df =  b.to_df()
    print(df)
    return

# =========================================================
# REFERENCE + SIGNAL LOGIC
# =========================================================
def get_trade_refs(df, ticker):
    d = df[df["Symbol"] == ticker].copy()

    d["Price"] = C.clean_price(d["Price"])
    d["trade_date"] = pd.to_datetime(d["trade_date"])

    latest_date = d["trade_date"].max()
    latest_day = d[d["trade_date"] == latest_date]

    has_buy = (latest_day["quantity"] > 0).any()
    has_sell = (latest_day["quantity"] < 0).any()

    if has_buy and has_sell:
        buy_ref = latest_day[latest_day["quantity"] > 0]["Price"].min()
        sell_ref = latest_day[latest_day["quantity"] < 0]["Price"].max()

    elif has_buy and not has_sell:
        buy_ref = latest_day[latest_day["quantity"] > 0]["Price"].min()
        sell_ref = buy_ref

    elif has_sell and not has_buy:
        sell_ref = latest_day[latest_day["quantity"] < 0]["Price"].max()
        buy_ref = sell_ref

    else:
        buy_ref = None
        sell_ref = None

    if buy_ref is not None:
        buy_ref = round(buy_ref, 2)
    if sell_ref is not None:
        sell_ref = round(sell_ref, 2)

    return buy_ref, sell_ref

def get_signal(cp, buy_ref, sell_ref):
    if sell_ref is not None and cp > sell_ref * 1.10:
        return "SELL"

    if buy_ref is not None and cp < buy_ref * 0.90:
        return "BUY"
    return "HOLD"

if __name__ == '__main__':
    orderFileTesting()

