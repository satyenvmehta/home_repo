
import os

from dataclasses import dataclass, field
from typing import List, Any

from pprint import pprint
from pprint import pprint as print

import numpy as np

import pandas as pd
from pandas import DataFrame
# # import numpy as np
# import pandas as pd

# import datetime
unittest = False

# from files_include import pos_file
# # from TradeUtil import BaseTrade1, BaseObjectItem, BaseTradeSymbol
# header_lines = 3

# from base_classes import BaseObject

# % Changes today - to recommend buy/sell
TodaysChange = 0
StrongBuy = 5
StrongSell = StrongBuy
Buy = StrongBuy-2
Sell = Buy
Hold = Buy -1

SellTh = 0.05 # 5 %
BuyTh = SellTh +  0.02 # 7%

SmallMrkCapValue = 200

def getDeltaPercentage(p1, p2):
    deptaP = 100 * (p1 - p2) / p1
    return deptaP

MFList = ['FAGIX',	'FBIOX',	'FDCPX',	'FDRXX',	'FHIFX',	'FHKCX',	'FIDSX',	'FIEUX',	'FNBGX',	'FOCPX',	'FPHAX',	'FRESX',	'FSAGX',	'FSAVX',	'FSCHX',	'FSCSX',	'FSDAX',	'FSDPX',	'FSELX',	'FSENX',	'FSHCX',	'FSLBX',	'FSLEX',	'FSPHX',	'FSPTX',	'FSRBX',	'FSRFX',	'FUMBX',	'FWRLX',	'FWWFX',]

'''
def map_lam():
    # Double all numbers using map and lambda
    numbers = (1, 2, 3, 4)
    result = map(lambda x: x + x, numbers)
    print(list(result))
    return



def get_load_fun_basedon_cls(cls):
    noClsParam = len(cls.__annotations__)
    lamfun = None
    if noClsParam == 1:
        lamfun = lambda x:cls(x[0])
    elif noClsParam == 2:
        lamfun = lambda x:cls(x[0], x[1] )
    elif noClsParam == 5:
        lamfun = lambda x:cls(x[0], x[1], x[2], x[3], x[4] )
    elif noClsParam == 10:
        lamfun = lambda x: cls(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9])
    elif noClsParam == 17:
        lamfun = lambda x: cls(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10], x[11], x[12], x[13], x[14], x[15], x[16])
    elif noClsParam == 18:
        lamfun = lambda x:cls(x[0], 	x[1], 	x[2], 	x[3], 	x[4], 	x[5], 	x[6], 	x[7], 	x[8], 	x[9], 	x[10], 	x[11], 	x[12], 	x[13], 	x[14], 	x[15], 	x[16], 	x[17])
    else:
        print("No method for Number of elements = ", noClsParam)
    return lamfun

def load_data_to_class_list(df:pd.DataFrame, cls)->list:
    lamfun = get_load_fun_basedon_cls(cls)

    if lamfun:
        return list(map(lamfun, df.values.tolist()))

    return None

@dataclass
class a1(object):
    a : int
    # b : str
    def __post_init__(self):
        return

'''

# if __name__ == '__main__':
#     a = a1(1)
#     # lamf = get_load_fun_basedon_cls(a1)
    # print(lamf)



# def crete_row_values_to_class( cls, row):
#     annos = cls.__annotations__
#     data_dict = {}
#     colid = 0
#     for name, typ in annos.items():
#         from TradeUtil import BaseTradeSymbol, BaseTrade, BaseTrades, BaseTradeStatus
#         data_dict[name] = typ(row[colid])
#         colid = colid + 1
#     cls_inst = cls.from_dict(data_dict)
#     return cls_inst
#
# def create_rows_to_class_list( cls, rows):
#     class_list = []
#     for row in rows:
#         cls_inst = crete_row_values_to_class(cls, row)
#         class_list.append(cls_inst)
#     return class_list

# def crete_row_values_to_class(cls, row):
#     annos = cls.__annotations__
#     data_dict = {}
#     colid = 0
#     for name, typ in annos:
#         data_dict[name] = typ(row[colid])
#         colid = colid+1
#     cls_inst = cls.from_dict(data_dict)
#
# def create_rows_to_class_list(cls, rows):
#     class_list = []
#     for row in rows:
#         cls_inst = crete_row_values_to_class(cls, row)
#         class_list.append(cls_inst)

'''

@dataclass
class BaseTrades(BaseReaderWriter):
    def __post_init__(self):
        super().__post_init__()
        self.cls = BaseTrade1
        self.uniqueCols = ['Symbol'] #,'Status',]
        self.read(header_lines, order_file)
        return
    def read(self, header_lines, order_file):
        super().read( header_lines, order_file)
        # for order in self.getBase():
        #     if isinstance(order, BaseTrade):
        #         order.setDescDetails()
        #     else:
        #         print("Cant custmize")

        return self.getBase()
    def findSymbol(self, sym):
        results = []
        for item in self.getBase():
            if isinstance(item, BaseTrade1):
                if item.Symbol == sym:
                    print(str(item.Symbol))
                    results.append(item)
        if len(results):
            return results
        return None
'''
#
# if __name__ == '__main__':
#     b = BaseTrades()
#     print(b.findSymbol('ZM'))

'''

class MyClass:
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['value1'], data_dict['value2'])

# Create a dictionary
data_dict = {'value1': 42, 'value2': 24}

# Create a class instance from the dictionary
my_instance = MyClass.from_dict(data_dict)

# Access the instance variables
print(my_instance.value1)  # Output: 42
print(my_instance.value2)  # Output: 24


BaseTrade1.__annotations__
{'Symbol': <class '__main__.BaseTradeSymbol'>, 'Status': <class 'base_classes.BaseObject'>}
BaseTrade1.__annotations__['Symbol']
<class '__main__.BaseTradeSymbol'>
type(BaseTrade1.__annotations__['Symbol'])
<class 'type'>
BaseTrade1.__annotations__['Symbol']
<class '__main__.BaseTradeSymbol'>
BaseTrade1.__annotations__['Symbol']('AAA')
BaseTradeSymbol(_item='AAA')
z = BaseTrade1.__annotations__['Symbol']('AAA')
z
BaseTradeSymbol(_item='AAA')
@dataclass
class BaseTradeSymbol(BaseObjectItem):
    def __post_init__(self):
        return
    def __str__(self):
        sym = "{:>15}mmmm".format(self.getBase())
        # print(sym)
        return sym
    
@dataclass
class BaseTrade1(BaseObject):
    Symbol : BaseTradeSymbol = None
    Status : BaseObject= None
    
typ = BaseTrade1.__annotations__['Symbol']
z = typ('AAA')
str(z)
'            AAAmmmm'

'''