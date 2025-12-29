# from common_include import *
from dataclasses import dataclass

import pandas as pd
from base_lib.core.base_classes import *
Debug_sym = "BLUE"

from base_lib.core.base_classes import BaseTradeSymbol, BaseTradePrice

@dataclass
class TransRequest(BaseObject):
    Symbol  : BaseTradeSymbol = None
    bs: BaseString = None

    reccomnd: BaseString = None
    # action  : BaseString = None
    # Qty: BaseInt = None
    # PercDiff: BaseFloat = None
    PerGnL: BaseFloat = None
    ActToSell : BaseString = None
    # PerGnL: BaseString = None
    Yield : BaseFloat = None
    price : BaseString = None
    lastP : BaseTradePrice = None


from TradeUtil import BaseTrades
@dataclass
class TransRequests(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        return

header = ["Symbol", "BS", "Recommend", "PerGnL",
          "ActToSell",  "Yield",
           "Price", "lastP"]

def append(b, t):
    bdf, bsm =  t.toDF(sep='|', header=header)
    b.export_df = pd.concat([b.export_df, bdf], ignore_index=True)
    return b

def tr():
    b = TransRequests()
    tr = TransRequest('t', 't', 'bs', 10, 'abc', 3, '3', 5)
    append(b, tr)
    tr1 = TransRequest('t', 't', 'bs', 10, 'abc', 3, '3', 5)
    append(b, tr1)

    print(b.export_df)

    print("Done..")

if __name__ == '__main__':
    tr()


