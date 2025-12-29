from dataclasses import dataclass

from base_lib.core.base_classes import *
from tp.market.get_price import get_market_price
#from ticker import TickersSet

Debug_Ticker = "PATH"
from base_lib.core.base_container_classes import  BaseSet, BaseList

from base_lib.core.files_include import rootdir, output_file, alt_output_file, ticker_file

from base_lib.core.base_classes import BaseTradeSymbol, BaseTradePrice
from base_lib.core.base_container_classes import BuySellSet
from tp.market.client_fe import MarketPrice

import main
from order import Orders, Order
from position import Positions, Position
from all_history import Historys #,  historySummary
from inteli_scan import InteliScans, InteliScan
from base_lib.core.common_include import getDeltaPercentage

tooFar2TradeThreshold = 5
BT = 12
thresholdP = {'B': BT, 'S': BT + 1}


# Debug_Ticker = Debug_sym

@dataclass
class Exception(BaseObject):
    Symbol: BaseObject
    reason: BaseObject
    action: BaseObject

from base_lib.core.common_include import BuyTh, SellTh
from tp_include import *

@dataclass
class Result(BaseObject):
    curr_ticker  : BaseTradeSymbol = None
    bs: BaseString = None

    reccomnd: BaseString = None
    # action  : BaseString = None
    Qty: BaseInt = None
    PercDiff: BaseFloat = None
    PerGnL: BaseFloat = None
    ActToSell : BaseString = None
    VPScore: BaseString = None
    IdleSecurity : BaseString = None
    # PerGnL: BaseString = None
    Yield : BaseFloat = None

    earningAlert: BaseInt = None
    price : BaseString = None
    lastP : BaseTradePrice = None
    TSML : BaseString = None
    category:  BaseString = None
    mcap: BaseString = None
    STRecomm: BaseString = None
    STDeltaP: BaseFloat = None

from TradeUtil import BaseTrades
@dataclass
class Results(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        return
@dataclass
class tkr_acct(BaseObject):
    tkr : BaseTradeSymbol
    acct : BaseString

    def getTicker(self):
        if isinstance(self.tkr, BaseObject):
            return self.tkr.getBase()
        return self.tkr
    def getAcct(self):
        return self.acct.getBase()

@dataclass
class tkr_action(BaseObject):
    curr_ticker  : BaseTradeSymbol
    action  : BaseString
    # bs_ext : BaseString

@dataclass
class TradeProcessing(BaseObject):
    orders: Orders = None
    historys: Historys = None

    def __post_init__(self):
        self.historys = Historys()
        self.hist_summ = self.historys
        self.positions = Positions()
        self.positions.setHistorys(self.historys)
        self.orders = Orders()
        self.inteli_scans = InteliScans()
        self.results = Results()
        self.vantages = self.inteli_scans
        self.bs_ext = ""
        self.marketPrices = None

        # self.result_df = None
        self.sep = ":"

        self.results.setUnitClass(Result)  # Soecial Class - not reading files but preparing here..

        earning = 'earningAlert' # + "ED as of " + str(Today('%b-%d'))
        self.header = ["Symbol" , "Action@Price_LastH_Price_Qty" , "Recommend",  "Qty", "PercDiff" ,  "PerGnL",
                       "ActToSell", "VPScore","IdleSecurity",  "Yield",
                         earning,  "Limit Price/Ref Hist Prc" , "lastP"  , "VP_Ind(T|S|M|L)",  \
                        "Category", "MrkCap", "STRecomm", "STDeltaP"]
        self.tkr_set = BaseSet()
        self.getVantageMissingPos()
        # self.getPositionNotTradedInLast()
        self.deltaP = 0
        return

    def printDuplicateOrders(self):
        self.orders.printDuplicateOrders()
        return

    def determineShortTermRecommend(self):
        self._debug()
        tkr = self.curr_ticker
        self.STRecomm = HOLD
        if not self.lastP:
            return
        if self.hist_summ.hasHistory(tkr) == False:
            return
        if self.hist_summ.getNoOfBusDaysSinceLastTrade(tkr) > ShortTermDays:
            return
        last_hist_price = self.hist_summ.getLastPrice(tkr)
        if not last_hist_price:
            return
        if isinstance(last_hist_price, BaseTradePrice):
            last_hist_price = last_hist_price.getBase()
        if isinstance(self.lastP, BaseTradePrice):
            lastP = self.lastP.getBase()
        else:
            lastP = self.lastP
        self.STDeltaP = round(getDeltaPercentage(lastP, last_hist_price), 2)

        if self.STDeltaP < -ShortTermGnLPercentageBuy:
            self.STRecomm = ShortTermBuy + self.buy_exist
            return
        if self.STDeltaP < -STLPerc:
            self.STRecomm = STBuyLimit + self.buy_exist
            return
        if self.positions.existsForSym(self.curr_ticker):
            if self.STDeltaP > ShortTermGnLPercentageSell:
                self.STRecomm = ShortTermSell + self.sell_exist
                return
            if self.STDeltaP > STLPerc:
                self.STRecomm = STSellLimit + self.sell_exist

        return

    def getPositionNotTradedInLast(self, days=60):
        uni_pos = self.positions.all_symbols
        idle_hist_syms = self.historys.idle_trade_qry(days)
        list(filter(lambda x: x in uni_pos.tolist(), idle_hist_syms))
        return
    def saveResults(self):
        if  len(self.results.export_df) <=0:
            print("No Results(self.results.export_df) to print")
            return

        self.results.assignFormats()
        # self.results.setDataFrame(self.result_df)
        listOfInterest = {'Results':self.results.getSelf(), 'Orders':self.orders.getSelf(), 'Postions': self.positions, 'Vantage': self.inteli_scans, 'History': self.historys ,  'HistorySummary': self.hist_summ.summary_df}

        self._saveResults(listOfInterest=listOfInterest, fileName=output_file, altFilename=alt_output_file)

        self.printDuplicateOrders()
        return

    def dupAction(self, action):
        self._debug()
        tkr_act = tkr_action(self.curr_ticker, action)
        rc = self.tkr_set.append(tkr_act)
        return rc

    def str2Numueric(self, s, exCh=None):
        if isinstance(s, BaseObject):
            s = s.getBase()
        if not isinstance(s, str):
            return s
        if exCh and  s and s.endswith(exCh):
            s = s.replace(exCh, "")
        if exCh and  s and s.startswith(exCh):
            s = s.replace(exCh, "")

        try:
            val = float(s)
        except:
            val = None
        return val

    def getSuggestedPrice(self, bs):
        self._debug()
        delta = 0.1
        rounding = 2
        if not bs:
            return 0
        if (bs.startswith("Buy") or bs.startswith("Adjust Buy")) and self.bs_ext.startswith('B'):
            delta = -.06
        elif (bs.startswith("Sell") or bs.startswith("Adjust Sell"))  and self.bs_ext.startswith('S'):
            delta = .05
        elif (bs.startswith("Buy") or bs.startswith("Adjust Buy")) and self.bs_ext.startswith('S'):
            delta = -delta
        elif (bs.startswith("Sell") or bs.startswith("Adjust Sell"))  and self.bs_ext.startswith('B'):
            delta = delta
        sugP = self.lastP
        suggested_price = 0
        if sugP:
            suggested_price = sugP*(1+delta)
            # suggested_price = round(suggested_price, 2)
        return suggested_price

    def printAction(self, bs, qty, price):
        self._debug()
        # if qty.startswith("None"):
        #     qty = None
        if (qty is None) and bs.startswith('Sell'):
            print( {"No Posn: Cant sell " : self.curr_ticker } )
            return None

        if self.curr_vant_obj:
            score = str(self.curr_vant_obj.score)
        else:
            score = 'NA'
        if not self.dupAction(bs):
            return None

        if not price:
            suggested_price = self.getSuggestedPrice(bs)
        else:
            if isinstance(price, BaseMoney):
                price = price.getBase()
            if isinstance(price, str):
                price = price.replace('$', '')
                try:
                    price = float(price)
                except:
                    price = 0

            suggested_price = price  #.replace('$',  '')
        suggested_price = round(suggested_price, 2)
        if self.hist_summ.hasHistory(self.curr_ticker):
            bs = bs + "@" + str(suggested_price).strip() + \
                 "_" + self.bs_ext + "_" + str(self.hist_summ.getLastPrice(self.curr_ticker)) + "_" + str(self.hist_summ.getLastQuantity(self.curr_ticker))
            if bs.startswith("Sell"):
                if isinstance(qty, BaseInt):
                    qty = qty.getBase()
                bs = bs + "_R" + str(int(qty))
        else:
            if self.bs_ext:
                bs = bs + "_" + self.bs_ext

        qty = self.str2Numueric(self.total_pos.toInt())
        deltaP = 0
        if self.deltaP != "NA":
            deltaP = round(self.str2Numueric(self.deltaP, "%"), 3)
        PerGnL = self.str2Numueric(self.PerGnL, "%")
        yieldVal = self.str2Numueric(self.yieldVal, "%")
        score = self.str2Numueric(score)
        # lastP = self.str2Numueric(self.lastP, "$")
        self.earningAlert = self.str2Numueric(self.earningAlert)

        if self.positions.isPennyStock(self.curr_ticker):
            penny = "_P"
        else:
            penny = None

        if penny:
            if isinstance(self.bsh, str):
                if not self.bsh.endswith(penny):
                    self.bsh = self.bsh + penny

        acts, ActToSell = self.historys.getActListToSell(self.curr_ticker, self.positions)
        # self.earningAlert.
        result = Result(self.curr_ticker ,bs,  self.bsh , qty, deltaP, PerGnL, \
            ActToSell, score, self.IdleSecurity,  yieldVal, \
            self.earningAlert, price ,self.lastP,  self.TSML,   self.category, self.mcap, self.STRecomm, self.STDeltaP)

        bdf, bs_msg = result.toDF(sep=self.sep, header=self.header)
        if not bdf.empty:
            self.results.export_df = pd.concat([self.results.export_df, bdf], ignore_index=True)
        return bs_msg

    def setPositionBasedAttr(self):
        if not self.curr_pos_obj:
            return
        # self.yieldVal = self.curr_pos_obj.Yield
        # self.EquityScore = self.curr_pos_obj.EquityScore
        # self.PerGnL = self.curr_pos_obj.PerGnL
        # self.lastP = self.curr_pos_obj.Last.getBase()
        return

    def print(self, msg):
        print(msg, width=1000),
        return
    def calculateRelativePerformance(self):
        print("TBD calculateRelativePerformance")
        # Use Vantage data for calc relative performance for each security in its group
        # for example - NVDA w.r.t XLK, TOL w.r.t. XLRE
        return

    def initDefaults(self):
        # print({"Init Defaults for : ": self.curr_ticker})
        # self.debug(self.curr_ticker)
        self.earningAlert = None
        self.lastP = 0
        self.yieldVal = 0
        self.IdleSecurity = "NA"
        self.PerGnL = 0
        self.mcap = None
        # self.curr_hist_objs = None
        self.curr_vant_obj = None
        self.bs_ext = ""
        self.TSML = "NA"
        self.total_pos = BaseFloat(0)
        self.curr_hist_obj = None
        self.curr_pos_obj = None
        return

    def initRowLevel(self):
        self.bsh = None
        self.curr_buy_order, self.curr_sell_order = None, None
        self.buy_exist , self.sell_exist  = "", ""
        self.STDeltaP, self.STRecomm = 0, HOLD
        self.setCurrOrdObjs()
        return

    def getBestPriceForSymbols(self, symbols):
        # symbols = ['DUFRY', 'MSFT', 'CSCO', 'TESTSYM']
        print("Getting Latest Prices for " + str(len(symbols)) + " symbols from Yahoo Finance")
        self.marketPrices = MarketPrice(symbols)
        return self.marketPrices

    def getBestPriceForSymbol(self):
        symbol = self.curr_ticker
        if self.lastP:
            return
        if self.curr_pos_obj:
            self.lastP = self.curr_pos_obj.Last.getBase()
            if self.lastP:
                # print({"Found Price from Positions for ": symbol, "Prices = ": self.lastP})
                return
        ord_based_lastP = self.orders.getLastPrice(symbol)
        if ord_based_lastP:
            self.lastP = ord_based_lastP.getBase()
            print({"Found Price from Orders for ": symbol, "Prices = ": self.lastP})
            return

        self.lastP = get_market_price(symbol) # self.marketPrices.getPrice(symbol)
        if self.lastP:
            print({"Found Price from MarketPrice for ": symbol, "Prices = ": self.lastP})
            return

        if self.hist_summ.hasHistory(self.curr_ticker):
            self.lastP = self.hist_summ.getLastPrice(self.curr_ticker)
        if self.lastP:
            print({"Found Price from history for ": symbol, "Prices = ": self.lastP})
        return
    def setActionParams(self):
        self.getBestPriceForSymbol()
        if isinstance(self.curr_pos_obj, Position):
            self.earningAlert = self.curr_pos_obj.earningAlert
            self.mcap = self.curr_pos_obj.MarketCap
        return

    def debug(self, str_val):
        if str_val == Debug_Ticker:
            print("Debug")
        return

    def _debug(self):
        self.debug(self.curr_ticker)
        return

    def getBuyNEWParams(self):
        self.bsh = "NEW"
        if self.lastP:
            if self.hist_summ.getLastPrice(self.curr_ticker):
                percDiff = 100 * (self.hist_summ.getLastPrice(self.curr_ticker) - self.lastP) / self.lastP
            else:
                percDiff = 0
        else:
            percDiff = 0
            self.bsh = "NA"
        if percDiff > 15:
            self.bsh = SB
        elif percDiff > 10:
            self.bsh = BB
        elif percDiff > 1:
            self.bsh = HOLD
        message = "BuyNEW"

        self.getBestPriceForSymbol()
        currP = self.lastP
        if not currP:
            return None, None
        if self.hist_summ.hasHistory(self.curr_ticker):
            h_qty = self.hist_summ.getLastQuantity(self.curr_ticker)
        else:
            h_qty = 1000 / currP   # Lets try for $1000 worth of shares
        qty = int(h_qty)
        bp = currP * 0.9  # 10% below last price
        bp = round(bp, 2)
        return bp, qty, message

    def Action(self, actionFlag, message, tradePrice=None, qty=None):
        self._debug()
        self.setActionParams()
        if not tradePrice:
            bp, bq = self.getBuyParams()
            sp, sq = self.getSellParams()
        # qty = self.getTradeQty()

        if actionFlag in ['BO']:
            if not self.positions.existsForSym(self.curr_ticker):
                tradePrice, qty, message = self.getBuyNEWParams()
                if not tradePrice:
                    return
            else:
                if self.positions.isSmallCap(self.curr_ticker):
                    self.bsh = "SMMrkCap"
                tradePrice = bp
                qty = bq
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
        self.setCurrOrdObjs()
        if self.bs_hint != "":
            if self.bsh:
                if self.bsh.find('(') < 0:
                    self.bsh = self.bsh + self.bs_hint
            else:
                self.bsh = "Hold*"
        msg = self.printAction( message, qty, tradePrice)
        if msg:
            self.print(msg)
        return

    def hasHistoryPrice(self):
        if not self.hist_summ.hasHistory(self.curr_ticker):
            return False
        return True

    def orderExists(self, sym, bs):
        return self.orders.exists(sym, bs)

    def retVals(self, lp,qty):
        return str(BaseMoney(lp)), BaseInt(qty)
        # return str(BaseMoney(lp)) + "/" + str(BaseMoney(hp)), str(BaseInt(qty))

    def _setNextBuySellRefPrices(self):
        self.lastAction = self.hist_summ.getLastAction(self.curr_ticker)
        self._setNextBuyPrice()
        self._setNextSellPrice()
        return
    def _setNextSellPrice(self):
        lp = self.hist_summ.getLastPrice(self.curr_ticker)
        if self.lastAction == 'B':
            np = lp * (1 + .1)
        else:
            np = lp * (1 + .05)
        self.nextSellPrice = round(np, 2)
        return

    def _setNextBuyPrice(self):
        lp = self.hist_summ.getLastPrice(self.curr_ticker)
        if self.lastAction == 'S':
            np = lp * (1 - .1)
        else:
            np = lp * (1 - .05)
        self.nextBuyPrice = round(np, 2)
        return

    def getBuyParams(self):
        if self.orderExists(self.curr_ticker, 'B'):   # No action required  -- Needs to validate Price
            return None, None
        if self.hasHistoryPrice():
            lp = self.getNextBuyPrice()
            qty = self.hist_summ.getLastQuantity(self.curr_ticker)  * 1.1
            self.debug(self.curr_ticker)
            return self.retVals(lp,  qty)
        return None, None

    def getSellParams(self):
        lp = self.nextSellPrice #self.hist_summ.getNextSellPrice(self.curr_ticker)
        # lp = hobj.getPrice() * (1 + SellTh)
        qty = self.hist_summ.getLastQuantity(self.curr_ticker) * 1.1
        if isinstance(self.curr_pos_obj, Position):
            self._debug()
            if self.total_pos.isPositive():
                qty = self.total_pos.getBase()
        return self.retVals(lp, qty)

    def getNextBuyPrice(self):
        return self.nextBuyPrice
    def getNextSellPrice(self):
        return self.nextSellPrice

    def print_recs(self, obj="ALL"):
        if (obj == 'Orders' or obj == 'ALL'):
            self.orders.print()
        if (obj == 'Position' or obj == 'ALL'):
            self.positions.print()
        if (obj == 'History' or obj == 'ALL'):
            self.historys.print()
        if (obj == 'IntelliScan' or obj == 'ALL'):
            self.inteli_scans.print()
        return

    def ValidateOrderLimitPrices(self):
        # if self.ifDeltaGTThreashold():
        self.Action("V", "Validate Buy/Sell Prices")
        return

    def isAnIdleSecurity(self):
        return self.IdleSecurity

    def analyzeSectorDistribution(self):
        self.setvantageObj()
        if isinstance(self.curr_vant_obj, InteliScan):
            self.category = self.curr_vant_obj.Category.getBase().replace(',','_')
        else:
            self.category = 'NA'
        return

    def get_curr_tkr_str(self):
        if isinstance(self.curr_ticker, BaseObject):
            tkr = self.curr_ticker.getBase()
        else:
            tkr = self.curr_ticker
        return tkr
    def getApproved2BuySuf(self):
        if self.historys.isApproved2Buy(self.get_curr_tkr_str()):
            self.suf = ""
        else:
            self.suf = "*"
        return self.suf

    def getApproved2SellSuf(self):
        if self.historys.isApproved2Sell(self.get_curr_tkr_str()):
            self.suf = ""
        else:
            self.suf = "*"
        return self.suf

    def setBuySellRec(self):
        self.bsh = "NA"
        self.delta = "NA"
        self.deltaP = "NA"
        if not self.hist_summ:
            return
        self.bs_ext = self.hist_summ.getLastAction(self.curr_ticker)
        if not self.bs_ext:
            self.bs_ext = ""
            return

        hp = self.hist_summ.getLastPrice(self.curr_ticker)
        if not hp:
            return

        if isinstance(self.lastP, float):
            cp = float(self.lastP)
        else:   # comeback str value
            return

        self.delta = (cp-hp)/hp
        self.deltaP = BasePercentage(self.delta*100)
        if self.delta > 2 * SellTh and self.total_pos.isPositive():
            self.bsh = SS + self.getApproved2SellSuf()
            return
        if self.delta > SellTh and self.total_pos.isPositive():
            self.bsh = SELL
            if self.bs_ext == 'S':
                self.bsh = SS
            self.bsh = self.bsh  + self.getApproved2SellSuf()
            return

        if self.delta < - 2 * BuyTh:
            self.bsh = SB + self.getApproved2BuySuf()
            return

        if self.delta < - BuyTh:
            self.bsh = BB
            if self.bs_ext == 'B':
                self.bsh = SB
            self.bsh = self.bsh + self.getApproved2BuySuf()
            return

        self.bsh = HOLD

        if self.positions.isSmallCap(self.curr_ticker):
            self.bsh = "SMMrkCap"
        return

    def setCurrOrdObjs(self):
        self.curr_buy_order, self.curr_sell_order = self.orders.get_bs_orders(self.curr_ticker)
        self.bs_hint = ""
        if self.curr_buy_order:
            self.bs_hint = B
            self.buy_exist = OrderExistSign
        if self.curr_sell_order:
            self.bs_hint = S
            self.sell_exist = OrderExistSign
        if self.curr_buy_order and self.curr_sell_order:
            self.bs_hint = BS
        if self.bs_hint != "":
            self.bs_hint = "(" +  self.bs_hint + ")"
        return

    def setCurrPosObj(self, acct=None):
        sym = self.curr_ticker
        self.curr_pos_obj = self.positions.getCurrentObj(sym, acct)
        self.setPositionBasedAttr()
        return

    def setvantageObj(self):
        vrlist = self.vantages.findSymbol(self.curr_ticker)
        if vrlist:
            self.curr_vant_obj = vrlist.getBase()[0]
        if self.curr_vant_obj:
            self.TSML = self.curr_vant_obj.getTSML()
        return

    def setAnayzeParams(self, acct=None):
        sym = self.curr_ticker
        self.debug(sym)
        self.total_pos = BaseFloat(self.positions.getTotalQty(self.curr_ticker))
        self.setCurrPosObj(acct)
        self.getBestPriceForSymbol()
        self.analyzeSectorDistribution()
        self._setHistBasedParams()
        return

    def _setHistBasedParams(self):
        if not self.positions.existsForSym(self.curr_ticker):
            self.IdleSecurity = "NA"
        else:
            self.IdleSecurity = str(self.historys.isAnIdleSymbol(self.curr_ticker))
        self.setBuySellRec()
        self._setNextBuySellRefPrices()
        self.determineShortTermRecommend()
        return

    def appendToTkrSet(self, ts, tkr):
        if tkr.startswith("adj "):
            return
        if tkr[0].isdigit():
            return
        ts.append(tkr)
        return

    def prepareListToOperate(self):
        self.accounts = self.positions.getHoldingAccounts()
        self.uniqPosList = self.positions.getUniqueSymbols()
        uords_tkr = self.orders.getUniqueSymbols()
        uhist_tkr = self.historys.getUniqueSymbols()
        tksSet = BaseSet()
        # all_tickers = TickersSet()
        import itertools
        for tkr in itertools.chain(uhist_tkr, uords_tkr):
            self.appendToTkrSet(tksSet, tkr)
        for tkr in self.uniqPosList:
            self.appendToTkrSet(tksSet, tkr)
        tkrs = tksSet.sort(key=None, reverse=False)
        tksSet.saveToCSV(ticker_file, header=["Symbol"])

        # self.idlePos_tkrs = sorted(list(set([x for x in self.uniqPosList if x not in uords_tkr])))
        self.tkr_acts = BaseList()
        print("Processing..")
        for tkr in tkrs:
            tobj = BaseTradeSymbol(tkr)
            if not tobj.validate():
                skip = "Skipped " + tkr
                print(skip)
                continue
            if tkr == Debug_Ticker:
                print("Debug break 1")
            posS = self.positions.getRecordsForSym(sym=tkr)
            if posS.notEmpty():
                for p in posS.getBase():
                    if isinstance(p, Position):
                        t = tkr_acct(p.Symbol, p.Account)
                        self.tkr_acts.append(t)
            else:
                t = tkr_acct(tkr, None)
                t.tkr = tkr
                self.tkr_acts.append(t)

        if self.tkr_acts.notEmpty():
            return self.tkr_acts
        else:
            return None

    def validateTicker(self, tkr_act):
        if not isinstance(tkr_act, tkr_acct):
            return False
        if isinstance(tkr_act.tkr, BaseObject):
            sym = tkr_act.tkr #.getBase()
        else:
            sym = BaseTradeSymbol(tkr_act.tkr)
        if not sym.validate():
            return False

        return True
    def analyzeBuySellAction(self):
        tkrActsList = self.prepareListToOperate()
        if not tkrActsList:
            return
        for tkr_act in tkrActsList.getBase():
            self.initDefaults()
            if not self.validateTicker(tkr_act):
                continue
            self.curr_ticker = tkr_act.getTicker()
            print({"Current Ticker ": self.curr_ticker})
            self.initRowLevel()
            if self.curr_ticker == Debug_Ticker:
                print("Debug break 2")
            self.setAnayzeParams(tkr_act.acct)
            if not self.hist_summ.hasHistory(self.curr_ticker) and not self.curr_pos_obj:
                self.Action("N", "Please investigate ticker - Never Traded this security")
                continue
            if self.isAnIdleSecurity() == "True":
                if self.hist_summ.hasHistory(self.curr_ticker):
                    self.Action(BS, "Buy/sell Order")
                    continue
            oobjs = self.orders.findOpenOrdersForSymbol(self.curr_ticker)
            if not oobjs:
                self.Action("BO", "Buy Order")
                self.Action("SO", "Sell Order")
                continue
            l = len(oobjs.getBase())
            if l > 0:
                print("Debug")
                self.orderBuySellAnalysis(oobjs)
        return

    def analyzeQQQ(self):
        pass

    def getLastHistPriceForOrder(self, oobj):
        if isinstance(oobj, Order):
            hp = self.hist_summ.getLastPrice(oobj.Symbol.getBase())
            if hp:
                return hp
            else:
                return None
        return None

    def bidTooFarFromHistory(self, oobj):
        if not self.hasHistoryPrice():
            return False, ""
        hp = self.getLastHistPriceForOrder(oobj)
        if not hp:
            return False, ""
        delatP = abs(getDeltaPercentage(hp, oobj.orderLimitPrice.getBase()))
        if thresholdP[oobj.buySell.getBase()] < delatP:
            return True, str(BasePercentage(delatP))
        return False, ""
    # NEW - Logic removal for comparing Order Limit Price with Hist Price
    # hp = self.getLastHistPriceForOrder(oobj)
    # if not hp:
    #     return False, ""
    # deltaH = abs(getDeltaPercentage(hp, oobj.orderLimitPrice.getBase()))
    # if thresholdP[oobj.buySell.getBase()] < deltaH:
    #     return True, str(BasePercentage(deltaH))

    def bidTooFarFromLast(self, oobj):
        # if not hp:
        delatP = abs(getDeltaPercentage(oobj.Last.getBase(), oobj.orderLimitPrice.getBase()))
        if thresholdP[oobj.buySell.getBase()] < delatP:
            return True, str(BasePercentage(delatP))
        return False, ""

    def historyBasedPricing(self, oobj):
        if not self.hasHistoryPrice():
            return False, None, None
        # sym = oobj.Symbol.getBase()
        if not self.hist_summ:
            return False, None, None

        tooFar, delata = self.bidTooFarFromHistory(oobj)
        if not tooFar:
            return False, None, None

        if oobj.isBuy():
            p = self.getNextBuyPrice()
        else:
            p = self.getNextSellPrice()

        if not p:
            p = oobj.orderLimitPrice.getBase()
        return "HP", delata, p


    def lastPriceBasedPricing(self, oobj):
        tooFar, delata = self.bidTooFarFromLast(oobj)
        if not tooFar:
            return False, None, None
        nextPriceDiff = 0.1 # 10 %
        if not self.lastP:
            self.lastP = 0
            print({"current symbol has issue" : self.curr_ticker})
        if oobj.isBuy():
            p = self.lastP - (self.lastP * nextPriceDiff)
        else:
            p = self.lastP + (self.lastP * nextPriceDiff)
        return "LP", delata, p

    def priceCalculator(self, oobj):
        p,  delata, price = self.lastPriceBasedPricing(oobj)
        if p:
            return p,  delata, price
        p, delata, price = self.historyBasedPricing(oobj)
        return p,  delata, price #price

    def orderBuySellAnalysis(self, oobjs):
        buy_sell = BuySellSet()
        for oobj in oobjs.getBase():
            # For a symbol
            if isinstance(oobj, Order):
                if not oobj.isOpen():
                    continue
            if not oobj.isGTC():
                continue
            # sym = oobj.Symbol.getBase()
            # print(oobj.buySell)
            buy_sell.append(oobj.buySell)
            farFrom, delata, price = self.priceCalculator(oobj)
            if farFrom:
                if oobj.buySell.getBase() == 'S':
                    bs = 'Sell'
                else:
                    bs = 'Buy'
                price = round(price, 2)
                self.Action("PC", "Adjust " + bs + " Price (" + delata.lstrip() + farFrom + ")", price, oobj.orderQty)
        if buy_sell.isBuyOnly():
            self.Action("SO", "Sell Order ")  # same for Buy
        if buy_sell.isSellOnly():
            self.Action("BO", "Buy Order ")  # same for Buy
        if buy_sell.isBuyAndSellSet():
            self.ValidateOrderLimitPrices()
        if buy_sell.multiBuyCounts():
            self.Action("BM", "Remove multi Buys")
        if buy_sell.multiSellCounts():
            self.Action("SM", "Remove multi Sell")
        return

    def getVantageMissingPos(self):
        upos = self.positions.getUniqueSymbols()
        u_van = self.inteli_scans.getUniqueSymbols()
        self.pos_not_in_vant = list(set([x for x in upos if x not in u_van]))
        self.pos_in_vant = list(set([x for x in upos if x in u_van]))
        # print(self.pos_not_in_vant)
        return

    def identifyOrdersTooFarFromCurrentPrice(self):
        # MODV Sell 70    At   34.95
        for order in self.orders.getBase():
            if order.isFilled():
                continue
            pos = self.positions.getBase().findSymbol(order.Symbol)
            if isinstance(pos, Position):
                perDiff = 100* (order.orderLimitPrice - pos.Last)/pos.Last
                if abs(perDiff) > tooFar2TradeThreshold:
                    exception = "Order Price Too (H|L) to Sell/Buy"

def Dbg_save_file(b):
    listOfInterest = {'Results': []}
    b._saveResults(listOfInterest=listOfInterest, fileName=output_file, altFilename=alt_output_file)
    exit(1)


def tp():
    b = TradeProcessing()
    # Dbg_save_file(b)
    # b.prepareListToOperate()
    b.resetDebug()
    b.analyzeBuySellAction()
    # b.analyzeSectorDistribution()
    b.saveResults()
    print("Done..")

    # b.report()

if __name__ == '__main__':
    # print(get_market_price("AAPL"))
    tp()


