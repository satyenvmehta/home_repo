import common_include as C

from TradeUtil import *

# Symbol: C.BaseTradeSymbol = None
# Last: C.BaseTradePrice = None
# Description:C.BaseString = None  # Buy 35 Limit at $26.25
# Status:C.BaseString = None
# Account:C.BaseString = None

from all_history import Historys #, historySummary
# from base_lib.core.files_include import pos_file
from tp.tp_include import SmallMrkCapValue


@C.dataclass
class Position(BaseTrade):
    Symbol: C.BaseTradeSymbol = None
    Last: C.BaseTradePrice = None
    PerChange: C.BasePercentage = None
    PerGnL: C.BasePercentage = None
    Quantity: C.BaseInt = None
    Account:C.BaseString = None
    DayRange:C.BaseString = None
    News:C.BaseString = None
    CloseValue: C.BaseTradePrice = None
    Change: C.BaseTradePrice = None
    Sector:C.BaseString = None
    Year_Range:C.BaseString = None
    Yield : C.BaseFloat = None
    Volume: C.BaseInt = None
    PurchasePrice: C.BaseTradePrice = None
    Value: C.BaseTradePrice = None
    TdyGnL: C.BaseTradePrice = None
    PerTdyGnL: C.BaseFloat = None
    GnL: C.BaseTradePrice = None
    EquityScore:C.BaseString = None
    PE: C.BaseFloat = None
    MarketCap:C.BaseString = None
    EarningsDate: C.BaseDate = None

    def __post_init__(self):
        self.setEarnigAlert()
        return

    def isAnIdlePosition(self):
        from all_history import Historys
        lastActDate = Historys.getLastActivityDate(self.Symbol)
        if lastActDate is not None:
            return False
        if isinstance(lastActDate, BaseDate):
            if  lastActDate.isOlderThan(60):
                return True
        return False

    def __str__(self):
        ps = str(self.Symbol) + "|" + str(self.Last)  + "|"+ str(self.Quantity)  + "|" + str(self.PerChange)
        return ps

    def setEarnigAlert(self):
        NoOfDays = self.EarningsDate.getNoDaysFromToday()
        if  NoOfDays < 10 and NoOfDays > -3:
            self.earningAlert = C.BaseInt(NoOfDays)
        else:
            self.earningAlert = None
        return

    # def isSmallCap(self):
    #     return self.Value.getBase() < SmallMrkCapValue

    @classmethod
    def from_dict(cls, data_dict):
        obj =  cls(data_dict['Symbol'],	data_dict['Last'],	data_dict['PerChange'],	data_dict['PerGnL'],
         data_dict['Quantity'],	data_dict['Account'],	data_dict['DayRange'],	data_dict['News'],
         data_dict['CloseValue'],	data_dict['Change'],	data_dict['Sector'],	data_dict['Year_Range'],
         data_dict['Yield'], data_dict['Volume'],	data_dict['PurchasePrice'],	data_dict['Value'],	data_dict['TdyGnL'],
         data_dict['PerTdyGnL'],	data_dict['GnL']
        , data_dict['EquityScore'],	data_dict['PE'],	data_dict['MarketCap'],	data_dict['EarningsDate']
                   )
        # obj.setEarnigAlert()
        return obj

@C.dataclass
class Positions(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        # sort_by = lambda x: x.Last
        # self.presetTrades(sort_by=sort_by, reverese=False)
        self.extra_columns = ['Ext Hrs Last', '% Ext Hrs Chg']
        self.cls = Position
        self.uniqueCols = [Symbol,	'Last',	'% Chg',	'Day Range',	'Sector',	'52 Wk Range',	'Volume',]
        self.readFile(self.cls, self.uniqueCols, header_lines=3, datafile=C.pos_file)
        self.acctSet = None
        self.getHoldingAccounts()
        df = self.getDF()
        self.all_symbols = df[Symbol].unique()
        self.historys = None
        return

    def setHistorys(self, hists):
        if isinstance(hists, Historys):
            self.historys = hists
        return

    def isAnIdlePosition(self, sym):
        found = self.getCurrentObj(sym)
        if found:
            hist = self.historys.isAnIdleSecurity(sym)
            # if isinstance(hist, historySummary):
            #     return hist.isAnIdleSecurity()
        return True

    def getTotalQty(self, sym):
        total = 0
        for pos in self.getBase():
            if pos.Symbol.getBase() == sym:
                total += pos.Quantity.getBase()
        return total
    def getFirstPos(self, sym):
        for pos in self.getBase():
            if pos.Symbol.getBase() == sym:
                return pos
        return None

    def getLastPrice(self, sym):
        p = self.getFirstPos(sym)
        if isinstance(p, Position):
            return p.Last.getBase()
        return 0

    def getPositionsValue(self, sym):
        total = 0
        for pos in self.getBase():
            if pos.Symbol.getBase() == sym:
                total += pos.Value.getBase()
        return total

    def isSmallCap(self, sym):
        return self.getPositionsValue(sym) < SmallMrkCapValue

    def isPennyStock(self, sym):
        found = False
        for pos in self.getBase():
            if not found and pos.Symbol.getBase() == sym:
                found = True
                if pos.isPennyStock():
                    return True
        return False

if __name__ == '__main__':
    b = Positions()
    print(b.existsForSym('AABV'))
    print(b.existsForSym('AAPL'))
    h = Historys()
    b.setHistorys(h)
    sym_list = ['CHGG', 'AAPL', 'AXP', 'INTC',  'AAOI',  'T', 'COIN', 'ZMZ', 'BLUE', 'AAOI', 'MCD']
    for sym in sym_list:
        print(sym)
        print(b.isSmallCap(sym))
        print(b.isPennyStock(sym))
        # print(b.isAnIdlePosition(sym))
    print(b.getLastPrice('AAPL'))
    print(b.getLastPrice('INTC'))
    b.printAccounts()

    if b.isPennyStock('AAPL'):
        print("Penny Stock")
    if b.isPennyStock('BLUE'):
        print("Penny Stock")
    # pos_list = b.getBase()
    res = b.findSymbol('T')
    for r in res.getBase():
        print(r)
    res.print()
    sym = 'AAOI' # 'AAOI'

    if b.isSmallCap(sym):
        print(b.getTotalQty(sym))
    for acct in b.getHoldingAccounts().getBase():
        found = b.getCurrentObj(sym, acct=acct)
        if found:
            print(str(acct) + " " + str(found))
    print(b.findSymbol('COIN'))
    print(b.findSymbol('ZMZ'))
