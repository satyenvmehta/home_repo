
# from base_lib.core.base_classes import *

import common_include as C

tooFar2TradeThreshold = 5
BT = 12
thresholdP = {'B': BT, 'S': BT + 1}

Debug_sym = "CEG"
Debug_Ticker = Debug_sym

@C.dataclass
class Exception_junk(C.BaseObject):
    Symbol: C.BaseObject
    reason: C.BaseObject
    action: C.BaseObject

# from base_lib.core.common_include import BuyTh, SellTh

@C.dataclass
class Action(C.BaseObject):
    actionFlag: C.BaseObject
    message: C.BaseObject
    tradePrice: C.BaseObject
    qty: C.BaseObject

    def __post_init__(self):
        # self.setActionParams()
        return

    def print(self):
        msg = self.printAction(self.actionFlag, self.message, self.qty, self.tradePrice)
        if msg:
            self.print()
        return

    def printAction(self, bs, qty, price):
        # self._debug()
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
            if isinstance(price, C.BaseMoney):
                price = price.getBase()
            if isinstance(price, str):
                price = price.replace('$', '')
                price = float(price)
            suggested_price = price  #.replace('$',  '')

        if self.last_hist_obj:
            bs = bs + "@" + str(suggested_price).strip() + \
                 "_" + self.bs_ext + "_" + str(self.last_hist_obj.Price.getBase()) + "_" + str(self.last_hist_obj.Quantity.getBase())
            if bs.startswith("Sell"):
                if isinstance(qty, C.BaseInt):
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

'''

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

'''