
from dataclasses import dataclass, fields
from typing import List, Any

from pprint import pprint
from pprint import pprint as print

# import pandas as pd
# from pandas import DataFrame
# import numpy as np
# import pandas as pd
#
# import datetime
#
# #
from base_lib.core.base_classes import *

# from base_classes import BaseObject, BaseObjectItem,  BaseString, BaseFloat, BaseMoney,  BaseCustomStatus, BasePercentage
from base_lib.core.base_container_classes import    BaseReaderWriter,  BaseSet,  BaseList, BaseContainer, BaseDict, BaseBuySell
# from common_include import order_file

# rootdir = 'C:\\Users\\Consultant\\OneDrive\\Satyen\\family\\vepar\\'
# import files_include
'''

def isMFSym(sym):
    # if self.getBase() == 'ILTB':
    #     return True
    if len(sym) == 5 and str(sym).startswith("F"):
        # print(self.getBase())
        return True
    return False

@dataclass
class BaseTradeSymbol(BaseObjectItem):
    def __post_init__(self):
        return
    def __str__(self):
        base_str = "{:>15}".format(self.getBase())
        return base_str
    def isMF(self):
        return isMFSym(self.getBase())
        # if len(self.getBase()) == 5 and str(self.getBase()).startswith("F"):
        #     return True
        # return False
    def __eq__(self, other):
        if isinstance(other, BaseObject):
            if self.getBase() == other.getBase():
                return True
        else:
            if isinstance(other, str):
                if self.getBase() == other:
                    return True
        return False


@dataclass
class BuySellSet(BaseSet):
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

@dataclass
class BaseTradePrice(BaseMoney):
    def __post_init__(self):
        super().__post_init__()
        return
    def __str__(self):
        return super().__str__()

'''

@dataclass
class TradeBuySell(BaseSet):
    pass

@dataclass
class BaseTrade(BaseObject):
    Symbol: BaseTradeSymbol = None
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

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['Symbol']) #, data_dict['Status'])


@dataclass  #
class BaseTrades(BaseReaderWriter):
    def __post_init__(self):
        super(BaseTrades, self).__post_init__()
        sort_by = lambda x: x.Symbol
        self.presetTrades(sort_by=sort_by)
        return

    def post_read(self):
        for item in self.getBase():
            if isinstance(item, self.cls):
                # item.setDescDetails()
                if self.getDebug():
                    print(str(item))
            else:
                print("Cant custmize")
        return

    def _read(self, header_lines, datafile):
        super().read( header_lines, datafile)
        self.post_read()
        return self.getBase()

    # percentage_format = "{:.2%}"
    # currency_format = "${:,.2f}"
    # def setClassMembersByTypes(self, cls):
    #     self.colFormats = BaseDict()
    #     for member, mtype in self.getClassMembers(cls).items():
    #         if mtype is BaseTradePrice:
    #             frmt = BaseTradePrice.format_str
    #         if mtype is BasePercentage:
    #             frmt = BasePercentage.format_str
    #         self.colFormats.append(member, frmt)
    #     return
    #
    # def getClassMembersTypes(self):
    #     return self.colFormats

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

    def presetTrades(self, sort_by=None, reverese=False):
        self.resetDebug()
        self.sort_by = sort_by
        self.reverse = reverese
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
        lst = self._getUniqueSymbols()
        noMF=[]
        for item in lst:
            if not isMFSym(item):
                noMF.append(item)
        return noMF

    def read(self, header_lines, data_file):
        super().read( header_lines, data_file)  # Get DF formated data
        self.postReadProcess()
        if self.getSortBy():
            self.sort_data(key=self.getSortBy(), reverse=self.reverse)
            # print("sorted data " + str(self.getSortBy()))
        return self.getBase()

    def getHoldingAccounts(self):
        # self.accts = BaseList()
        if self.acctSet:
            return self.acctSet

        self.acctSet = BaseSet()
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

    def getRecordsForSym(self, sym=None):
        filt_pos = BaseList()
        for pos in self.getBase():
            if isinstance(pos, self.cls):
                if pos.Symbol.equals(sym):
                    filt_pos.append(pos)
        return filt_pos

    def getCurrentObj(self, sym, acct=None):
        objs = self.findSymbol(sym)
        if not objs:
            return None

        if objs.isEmpty():
            return None
        foundObj = None
        if objs.size() == 1:
            foundObj = objs.getFirst()
        if not acct:
            return foundObj

        for obj in objs.getBase():
            if isinstance(obj, self.cls):
                if isinstance(acct, BaseObject):
                    acct = acct.getBase()
                if obj.Account.getBase() == acct:
                    bestMatch = obj
                    return bestMatch
        return foundObj

    def findSymbol(self, sym, bs=None):
        results = BaseList()
        if not self.getBase():
            return
        if isinstance(sym, BaseObject):
            sym = sym.getBase()
        for item in self.getBase():
            if isinstance(item, BaseTrade):
                if item.Symbol.getBase() == sym:
                    if not bs:
                        results.append(item)
                    else:
                        if bs == item.getBuySell():
                            results.append(item)
        if results.isEmpty():
            return None
        return results

@dataclass
class OrderSampleClass( BaseTrade):
    Symbol : BaseTradeSymbol = None
    Last : BaseTradePrice = None
    Description : BaseString= None   # Buy 35 Limit at $26.25
    Status : BaseCustomStatus= None
    Account : BaseString= None
    def __post_init__(self):
        return

    def getBuySell(self):
        return "B"

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['Symbol'], data_dict['Last'], data_dict['Description'], data_dict['Status'], data_dict['Account'])

@dataclass
class OrdersSampleClass(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        return

    def getLastPrice(self, sym):
        ords = self.findSymbol(sym)
        if not ords:
            return None
        ord = ords.getFirst()
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
    return

if __name__ == '__main__':
    orderFileTesting()



    #
    # print(b.getDetailsBySymbol('AAPL'))
    # print(b.getUniqueRows())

# def reading_lorders(df:pd.DataFrame)->list:
#     return list(map(lambda x:Order(x[0], x[1], x[2], x[3], x[4] ),df.values.tolist()))
# if __name__ == '__main__':
#     b = Orders()
#     order_list = b.read()
#     b.print()
#
#     row2Examin = 16
#     offset = header_lines+1+1
#     actual_row = row2Examin-offset
#     print(order_list[actual_row])
#     results = b.getDetailsBySymbol('BTBT', Order)
#     for res in results.item:
#         print(res)
#
#     results = b.getDetailsBySymbol('BTBT123', Order)
#     for res in results.item:
#         print(res)


    # Symbol : BaseObject = field(repr=False)
    # Last : BaseObject= field(repr=False)
    # Description : BaseObject= field(repr=False)
    # Status : BaseObject= field(repr=False)
    # Account : BaseObject= field(repr=False)

# @dataclass
# class Orders(BaseDF):
#     def read(self):
#         fo = FileObject(order_file)
#         # index_col = 'Symbol'
#         df = fo.read( skip=header_lines)
#         self.item = load_data_to_class_list(df, Order)
#         return self.item


    # def setBuySell(self, bs):
    #     if bs == "Buy":
    #         self.buySell = "B"
    #     else:
    #         self.buySell = "S"
    #     # print(self.__dict__)
    #     print(str(self))
    #     # print(self.getBuySell())

    # def findSymbol(self, sym, bs=None):
    #     results = super().findSymbol(sym)
    #     if not results:
    #         return None
    #     if not bs:
    #         return results
    #
    #     nresults = BaseList()
    #     for item in results.getBase():
    #         if isinstance(item, self.cls):
    #             if item.getBuySell()  == bs:
    #                 nresults.append(item)
    #     return nresults