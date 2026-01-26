    # ai_objs = b.findSymbol('AI')

    # for item in ai_objs:
    #     print(str(item))
    # lastBuyPriceObj = b.getRefObjForSymbol('AI', bs="B")
    # # print(str(lastBuyPriceObj.Price))
    # lastSellPriceObj = b.getRefObjForSymbol('AI', bs="S")

    # sai = sorted(ai_objs, key=lambda x: x.Date, reverse = True)
    # for item in sai:
    #     print(str(item) + "..")
    # print(b.findSymbol('AI'))
    # print(b.findSymbol('ZMZ'))

    # row2Examin = 16
    # b.examinRow(row2Examin)
    #
    # print(b.getDetailsBySymbol('AAPL'))
    # print(b.getUniqueRows())

#
# @dataclass
# class Historys(BaseDF):  # Knowingly mis-spelled
#     def read(self):
#         fo = FileObject(hist_file)
#         # index_col = 'Symbol'
#         df = fo.read( skip=header_lines)
#         self.item = load_data_to_class_list(df, History)
#         return self.item
#
#     def getDetailsBySymbol(self, symbol):
#         for item in self.item:
#             if isinstance(item, History):
#                 if item.Symbol == symbol:
#                     return item
#         return None
#
#
#
#
#
# if __name__ == '__main__':
#     b = Historys()
#     pos_list = b.read()
#     # b.print()
#     row2Examin = 18
#     offset = header_lines+1+1
#     actual_row = row2Examin-offset
#     print(pos_list[actual_row])
#     print(b.getDetailsBySymbol('AAPL'))

'''
 def resetForNextSym(self, sym=None):
        self.lastH = None
        self.lastAction = ""
        # self.acctSet = None
        self.nextBuyPrice = None
        self.nextSellPrice = None
        self.lastPrice = 0.0
        self.lastQuantity = 0.0
        self.lastBuyRef = None
        self.lastSellRef = None
        self.refObjs = []
        # if sym:
        #     self.setForNextSym(sym)
        return

    def getRefObjsForSymbol(self, sym):
        return self.refObjs
    # def hasHistoryPrices(self):
    #     if self.refObjs:
    #         if self.refObjs[0] and self.refObjs[1]:
    #             return True
    #     return False

    def _setLastObjForSymbol(self, sym):
        # self.resetForNextSym()
        self.refObjs.append(self.getBuyRefFor(sym))
        self.refObjs.append(self.getSellRefFor(sym))
        self.lastBuyRef = self.getNextBuyRefPrice()
        self.lastSellRef = self.getNextSellRefPrice()
        return self.refObjs

    def _getLastObjForSymbol(self, sym):
        self.lastH = self._getRefObjForSymbol(sym)
        self._setLastPrice()
        self._setLastAction()
        return self.lastH

    def _setLastPrice(self):
        if self.lastH:
            self.lastPrice = self.lastH.getPrice()
            self.lastQuantity = self.lastH.getQuantity()

    def getLastObjForSymbol(self, sym):
        return self.lastH

    def getLastPrice(self):
        return self.lastPrice
    def getLastQuantity(self):
        return self.lastQuantity

    def getRefObjForSymbol(self, sym):
        return self.getLastObjForSymbol(sym)

    def setForNextSym(self, sym):
        self._getLastObjForSymbol(sym)
        self._setLastAction()
        self._setNextBuySellRefPrices(sym)
        self._setLastObjForSymbol(sym)
        return

    def _getRefObjForSymbol(self, sym, bs=None):
        recs = self.findSymbol(sym, bs)
        if not recs:
            return None
        if recs.isEmpty():
            return None

        sobjs = recs.sort(key=lambda x: x.Date, reverse=True)
        if not bs:
            return sobjs[0]

        for obj in sobjs:
            if isinstance(obj, self.cls):
                match = obj.matchesRefObj(bs)
                if match:
                    return match
        last_hobj = sobjs[0]
        return last_hobj

    def getBuyRefFor(self, sym):
        hobj = self._getRefObjForSymbol(sym, bs="B")
        if hobj:
            return hobj
        return self._getRefObjForSymbol(sym, bs="S")

    def getSellRefFor(self, sym):
        hobj =  self._getRefObjForSymbol(sym, bs="S")
        if hobj:
            return hobj
        return self._getRefObjForSymbol(sym, bs="B")

    def _setNextBuySellRefPrices(self, sym):
        self._setNextBuyPrice(sym)
        self._setNextSellPrice(sym)
        return

    def _setNextBuyPrice(self, sym):
        if not self.lastH:
            return None
        if not self.lastH:
            self.getLastObjForSymbol(sym)
        if not self.lastH:
            return None
        lp = self.lastH.Price.getBase()
        if self.lastAction.__eq__('S'):
            np = lp * (1 - .1)
        else:
            np = lp * (1 - .05)
        self.nextBuyPrice = round(np, 2)
        return self.nextBuyPrice

    def getNextBuyRefPrice(self):
        return self.nextBuyPrice
    def getNextSellRefPrice(self):
        return self.nextSellPrice

    def _setNextSellPrice(self, sym):
        if not self.lastH:
            self.getLastObjForSymbol(sym)
        if not self.lastH:
            return None
        lp = self.lastH.Price.getBase()
        if self.lastAction.__eq__('B'):
            np = lp * (1 + .1)
        else:
            np = lp * (1 + .05)
        self.nextSellPrice = round(np, 2)
        return self.nextSellPrice

    def _setLastAction(self):
        if self.lastH:
            if self.lastH.isBuy():
                self.lastAction = "B"
            else:
                self.lastAction = "S"
        else:
            self.lastAction = ""
        return

    def getLastAction(self):
        return self.lastAction
'''

    # obj = b.getSummaryForSymbol(sym)
    # if obj:
    #     # print(obj.getSummary())
    #     print( {"==============" : sym, "================" : "" })
    #     print(obj.getNextBuyPrice())
    #     print(obj.getNextSellPrice())
    #     print(obj.getLastPrice())
    #     print(obj.getLastQuantity())
    #     print(obj.getLastAction())
    #     print(obj.getBuyRef())
    #     print(obj.getSellRef())
    #     print(obj.getRefObjs())
    #     print(obj.isAnIdleSecurity())


    # def findBuySellParams(self, bs):
    #     self._debug()
    #     if self.orderExists(self.curr_ticker, bs):   # No action required
    #         return None # Nothing to do.. Should NOt COME Here
    #     if not self.curr_pos_obj:
    #         if bs == 'S':
    #             return None    # No posing - nothing to sell
    #
    #     if not self.hist_summ:
    #         return None
    #     if bs == 'S':
    #         hobj = self.hist_summ.getSellRef(self.curr_ticker)
    #     else:
    #         hobj = self.hist_summ.getBuyRef()
    #     return hobj

# @dataclass
# class historySummary(BaseObject):
#     historys : any #= None
#     sym: C.BaseTradeSymbol #= None
#
#     def _initbase(self):
#         self.lastH = None
#         self.lastAction = ""
#         self.nextBuyPrice = 0
#         self.nextSellPrice = 0
#         self.lastPrice = 0.0
#         self.lastQuantity = 0.0
#         self.lastBuyRef = None
#         self.lastSellRef = None
#         self.lastActivityDate = None
#         self.total_buy_qty  = 0
#         self.total_sell_qty = 0
#         self.total_buy_amt  = 0
#         self.total_sell_amt = 0
#         self.avg_buy_price  = 0
#         self.avg_sell_price = 0
#         self.total_gain_loss      = 0
#         self.total_gain_loss_perc = 0
#         self.avg_gain_loss_perc   = 0
#         self.refObjs = []
#         return
#     def __post_init__(self):
#         self._initbase()
#         self.setForNextSym()
#         return
#     def isAnIdleSecurity(self):
#         return self.history.isAnIdleSecurity()
#
#     def getLastObj(self):
#         return self.lastH
#
#     def getRefObjs(self):
#         return self.refObjs
#     def getBuyRef(self):
#         return self.refObjs[0]
#     def getSellRef(self):
#         return self.refObjs[1]
#
#     def setForNextSym(self):
#         self._setLastObj()
#         self._setBuyRef()
#         self._setSellRef()
#         return
#
#     def _setSummary(self):
#         if self.lastQuantity > 0:
#             self.total_buy_qty = self.total_buy_qty + self.lastQuantity
#             self.total_buy_amt = self.total_buy_amt + self.lastH.getAmount()
#         else:
#             self.total_sell_qty = self.total_sell_qty + self.lastQuantity
#             self.total_sell_amt = self.total_sell_amt + self.lastH.getAmount()
#         return
#     # def prepareSummary(self):
#     #     self._setSummary()
#     #     return self
#
#     def _setLastObj(self):
#         self.lastH = self._getRefObj()
#         if self.lastH:
#             self.lastPrice = self.lastH.getPrice()
#             self.lastQuantity = self.lastH.getQuantity()
#             self._setNextBuySellRefPrices()
#             self._setLastAction()
#             self._setLastActivityDate()
#             # self.()_setSummary
#         return
#
#     def _setLastActivityDate(self):
#         self.lastActivityDate = self.lastH.Date
#
#     def _setLastAction(self):
#         if self.lastH.isBuy():
#             self.lastAction = "B"
#         else:
#             self.lastAction = "S"
#         return
#
#     # def _setBuyRef(self):
#     #     hobj = self._getRefObj(bs="B")
#     #     if not hobj:
#     #         hobj = self._getRefObj(bs="S")
#     #     self.refObjs.append(hobj)
#     #     return
#     # def _setSellRef(self):
#     #     hobj =  self._getRefObj(bs="S")
#     #     if not hobj:
#     #         hobj = self._getRefObj(bs="B")
#     #     self.refObjs.append(hobj)
#     #     return
#
#     def _process_each_rec(self):
#         recs = self.historys.findSymbol(self.sym)
#         sobjs = recs.sort(key=lambda x: x.Date, reverse=True)
#         for obj in sobjs:
#             if isinstance(obj, History):
#                 self.hist_summ.append(obj)
#
#         if isinstance(obj, History):
#             self.historys.append(obj)
#         return
#     # def _getRefObj(self, bs=None):
#     #     recs = self.historys.findSymbol(self.sym, bs)
#     #     if not recs:
#     #         return None
#     #     if recs.isEmpty():
#     #         return None
#     #
#     #     sobjs = recs.sort(key=lambda x: x.Date, reverse=True)
#     #     if not bs:
#     #         return sobjs[0]
#     #
#     #     for obj in sobjs:
#     #         if isinstance(obj, History):
#     #             match = obj.matchesRefObj(bs)
#     #             if match:
#     #                 return match
#     #     last_hobj = sobjs[0]
#     #     return last_hobj
#     def isAnIdleSecurity(self):
#         if not self.lastActivityDate:
#             return True
#         if self.lastActivityDate.isOlderThan(45):
#             return True
#         return False