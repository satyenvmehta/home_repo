# from common_include import *
import pandas as pd
from base_lib.core.base_classes import *

# from TradeUtil import BaseBuySell
# from base_container_classes import BaseSet, BaseList
# from base_classes import BaseInt, BaseCustomStatus, BaseBuySell, BasePercentage
# from base_classes import BaseObject, BaseObjectItem,  BaseString, BaseFloat, BaseMoney
from base_lib.core.base_container_classes import BaseList, BaseReaderWriter, BaseSet, BaseList, BaseContainer, BaseDict

from base_lib.core.files_include import rootdir, output_file, alt_output_file

from base_lib.core.base_classes import BaseTradeSymbol, BaseTradePrice
from base_lib.core.base_container_classes import BuySellSet
from tp.market.client_fe import MarketPrice

import main
from order import Orders, Order
from position import Positions, Position
from all_history import Historys, History
from inteli_scan import InteliScans, InteliScan

tooFar2TradeThreshold = 5
BT = 12
thresholdP = {'B': BT, 'S': BT + 1}

Debug_sym = "CEG"
Debug_Ticker = Debug_sym

@dataclass
class Exception(BaseObject):
    Symbol: BaseObject
    reason: BaseObject
    action: BaseObject

from base_lib.core.common_include import BuyTh, SellTh

@dataclass
class Action(BaseObject):
    actionFlag: BaseObject
    message: BaseObject
    tradePrice: BaseObject
    qty: BaseObject

    # bsh: BaseObject
    # curr_ticker: BaseObject
    # curr_price: BaseObject
    # positions: BaseObject
    # orders: BaseObject
    # history: BaseObject
    # inteli_scan: BaseObject
    # market_price: BaseObject
    # buyTh: BaseObject
    # sellTh: BaseObject
    # exception: BaseObject
    # debug: BaseObject
    # debug_sym: BaseObject

    def __post_init__(self):
        self.setActionParams()
        return

    def print(self):
        msg = self.printAction(self.actionFlag, self.message, self.qty, self.tradePrice)
        if msg:
            self.print(msg)
        return

    def printAction(self, bs, qty, price):
        self._debug()
        # if qty.startswith("None"):
        #     qty = None
        if (qty is None) and bs.startswith('Sell'):
            print( "No Posn: Cant sell ") # + self.curr_ticker.getBase() )
            return None

        if self.curr_vant_obj:
            score = str(self.curr_vant_obj.score)
        else:
            score = 'NA'
        if not self.dupAction(bs):
            return "Dup action"

        if not price:
            suggested_price = self.getSuggestedPrice(bs)
        else:
            if isinstance(price, BaseMoney):
                price = price.getBase()
            if isinstance(price, str):
                price = price.replace('$', '')
                price = float(price)
            suggested_price = price  #.replace('$',  '')

        if self.last_hist_obj:
            bs = bs + "@" + str(suggested_price).strip() + \
                 "_" + self.bs_ext + "_" + str(self.last_hist_obj.Price.getBase()) + "_" + str(self.last_hist_obj.Quantity.getBase())
            if bs.startswith("Sell"):
                if isinstance(qty, BaseInt):
                    qty = qty.getBase()
                bs = bs + "_R" + str(int(qty))
        else:
            bs = bs + "_" + self.bs_ext


        qty = self.str2Numueric(self.total_pos.toInt())
        deltaP = self.str2Numueric(self.deltaP, "%")
        PerGnL = self.str2Numueric(self.PerGnL, "%")
        yieldVal = self.str2Numueric(self.yieldVal, "%")
        score = self.str2Numueric(score)
        # lastP = self.str2Numueric(self.lastP, "$")
        self.earningAlert = self.str2Numueric(self.earningAlert)
        # self.earningAlert.
        result = Result(self.curr_ticker ,bs,  self.bsh , qty, deltaP, PerGnL, \
            score, self.EquityScore,  yieldVal, \
            self.earningAlert, price ,self.lastP,  self.TSML,   self.category, self.mcap)

        bdf, bs_msg = result.toDF(sep=self.sep, header=self.header)
        self.results.export_df = pd.concat([self.results.export_df, bdf], ignore_index=True)
        return bs_msg


def Action(self, actionFlag, message, tradePrice=None, qty=None):
    self._debug()
    self.setActionParams()
    if not tradePrice:
        bp, bq = self.getBuyParams()
        sp, sq = self.getSellParams()
    # qty = self.getTradeQty()

    if actionFlag in ['BO']:
        if not self.positions.existsForSym(self.curr_ticker):
            self.bsh = "NEW"
            tradePrice, qty = self.getBuyNEWParams()
            if not tradePrice:
                return
        else:
            if self.positions.isSmallCap(self.curr_ticker):
                self.bsh = "SMMrkCap"
            tradePrice = bp
            qty = bq
        # bo_msg = self.printAction(actionFlag, "Buy", bq, bp)
        # so_msg = None

    if actionFlag in ['SO']:
        if not self.positions.existsForSym(self.curr_ticker):
            return
        if self.positions.isSmallCap(self.curr_ticker):
            self.bsh = "SMMrkCap"

        tradePrice = sp
        qty = sq

    if actionFlag in ['BM', 'SM']:
        tradePrice = None
        qty = sq
        # multi_msg = self.printAction(actionFlag, message, sq, None)

    if actionFlag.startswith("PC"):
        tradePrice = None
        # pc_msg = self.printAction(actionFlag, message, str(qty), None)  #str(lp))


    return