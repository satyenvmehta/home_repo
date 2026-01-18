
# from base_classes import *

'''
Symbol	Last	TradeDescription	            Status	Account	Order Number
AI     26.88	'Buy 50 Limit at $26.55'  	"FILLED AT $26.55"	ROLLOVER IRA (224916532)	I07NHLPL
'''

import common_include as C
from tp.TradeUtil import BaseTrade, BaseTrades, Symbol
from tp.lib.tp_classes import BaseTradeSymbol, BaseTradePrice, BaseCustomStatus, BaseBuySell

import numpy as np

header_lines=3

#  Adjust Buy Price  or Adjust Sell Price  Parameters
BT=12
thresholdP = {'B':BT, 'S' : BT+1}
@C.dataclass
class Order(BaseTrade):
    Symbol : BaseTradeSymbol = None
    Last : BaseTradePrice = None
    Description : C.BaseString= None   # Buy 35 Limit at $26.25
    Status : BaseCustomStatus= None
    Account : C.BaseString= None
    TIF:C.BaseString = None
    OrderNum :C.BaseString = None

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['Symbol'], data_dict['Last'],  data_dict['Description'], data_dict['Status'], data_dict['Account']
                   , data_dict['TIF'], data_dict['OrderNum'])
    def __post_init__(self):
        self.setDescDetails()
        return
    def isGTC(self):
        return self.TIF.getBase() == 'GTC'
    def __str__(self):
        bs = str(self.buySell)
        qty = "{:<5}".format(str(self.orderQty))
        lprc = "{:>7}".format(str(self.orderLimitPrice))
        ps = str(self.Symbol) + " " + str(bs)  + str(qty)  + " At " + str(lprc) + " " + str(self.getStatus())
        return ps

    def setDescDetails(self): # Buy 35 Limit at $26.25
        d_parts = str(self.Description).rstrip().split(' ')
        if d_parts[0] == 'Exchange':  # Skip MF exchanges to monitor
            return
        self.buySell = BaseBuySell(d_parts[0])
        self.orderQty = C.BaseInt(d_parts[1])
        lastval = d_parts[len(d_parts)-1]

        if not lastval.startswith("$"):
            lastval = self.Last.getBase()
        else:
            lastval = lastval.replace('$', '')
        self.orderLimitPrice = BaseTradePrice(lastval)
        # print(str(self))
        return

    # def bidTooFarFromLast(self, hp=None):
    #     from base_lib.core.common_include import getDeltaPercentage
    #     if not hp:
    #
    #     delatP = abs(getDeltaPercentage(self.Last.getBase(), self.orderLimitPrice.getBase()))
    #     if thresholdP[self.buySell.getBase()]  < delatP:
    #         return True, str(BasePercentage(delatP))
    #     return False, ""

    def isOpen(self):
        return self.Status.isOpen()
    def isFilled(self):
        return self.Status.isFilled()

    def getBuySell(self):
        return self.buySell.getBase()

    def getStatus(self):
        status = self.Status.getBase()
        if status:
            return status
        # if isinstance(status, str):
        #     st_words = status.split(' ')
        #     if st_words[0] in ['FILLED', 'OPEN', "O"]:
        #         return st_words[0]
        #     if st_words in ['PARTIALLY FILLED', 'VERIFIED CANCELLED']:
        #         return st_words[1]
        # print( {"{str(self)} Unknown Status " : status})
        return "NA"

    def getSymbol(self):
        return self.Symbol.getBase()


    def isBuy(self):
        bs = self.getBuySell()
        if bs == 'B':
            return True
        else:
            return False


@C.dataclass
class Orders(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        self.cls = Order
        self.uniqueCols = ['Symbol',	'Last',	'Trade Description',	'Status',]
        header_lines = 3
        from base_lib.core.files_include import order_file
        self.readFile(self.cls, self.uniqueCols, header_lines, order_file)
        df = self.getDF()
        self.all_symbols = np.sort(df[Symbol].unique())
        return

    def getLastPrice(self, sym):
        ords = self.findSymbol(sym)
        if not ords:
            return None

        ord = ords.getFirst()
        if isinstance(ord, Order):
            return ord.Last
        return None

    def findOpenOrdersForSymbol(self, sym):
        res = self.findSymbol(sym)
        if not res:
            return None
        nres = C.BaseList()
        for item in res.getBase():
            if isinstance(item, Order):
                if item.isOpen():
                    nres.append(item)
        if nres.size() == 0:
            return None
        return nres
    def get_bs_orders(self, sym):
        res = self.findSymbol(sym, 'B')
        if not res:
            bo = None
        else:
            bo = res.getFirst()
        res = self.findSymbol(sym, 'S')
        if not res:
            so = None
        else:
            so = res.getFirst()
        return bo, so

    def isMultipleOrders(self, sym, bs):
        res = self.findSymbol(sym, bs)
        if not res:
            return False
        if res.size() > 1:
            return True
        return False
    def exists(self, sym, bs):
        res = self.findSymbol(sym, bs)
        if not res:
            return False
        if res.size() > 1:
            print({"Multiple Orders" : res.size()})
            # return True
        if res.size() > 0:
            for ord in res.getBase():
                if isinstance(ord, Order):
                    if ord.isOpen():
                        return True
        return False
    # del print

    def printDuplicateOrders(self):
        print("Duplicate Orders - checking")
        for sym in self.all_symbols:
            if isinstance(sym, str):
                for bs in ['B', 'S']:
                    res = self.findSymbol(sym, bs)
                    if not res:
                        continue
                    if res.size() > 1:
                        cnt = 0
                        price = 0
                        for ord in res.getBase():
                            if isinstance(ord, Order):
                                if price == 0:
                                    price = ord.orderLimitPrice.getBase()
                                if ord.isOpen():
                                    cnt += 1
                                if cnt > 1:
                                    if bs == 'B' and price > ord.orderLimitPrice.getBase():
                                        price = ord.orderLimitPrice.getBase()
                                    elif bs == 'S' and price < ord.orderLimitPrice.getBase():
                                        price = ord.orderLimitPrice.getBase()

                        if cnt > 1:
                            print(f"Sym: {sym} Count: {res.size()} BS: {bs}")
                            # print(sym,  ":", res.size(), "BS:",  bs)
        print("Duplicate Orders - Done")
        return

    # def post_read(self):
    #     print("Custmizing")
    #     return

def initOrdersParams():
    for ord in ords.getBase():
        if isinstance(ord, Order):
            if ord.isFilled():
                print(str(ord))
    for ord in ['TGT', 'IRBT', 'ARRY']:
        print({f'{ord} B' : ords.exists(ord, 'B')})
    return ords

def orderFileTesting():
    b = initOrdersParams()
    # print({"AAOI S " : b.findSymbol('AAOI', bs='S').getFirst()} )
    print(b.findSymbol('XBI'))
    row2Examin = 16
    b.examinRow(row2Examin)
    b.saveToFile("TestSample1.xlsx")
    acct = b.getHoldingAccounts()
    print(acct)
    return


if __name__ == '__main__':
    ords = Orders()
    ords.printDuplicateOrders()
    # orderFileTesting()


