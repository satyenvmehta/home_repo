from market.client  import getPricesFor

from core.base_include import *

from dataclasses import dataclass

from market.get_price import get_market_price


@dataclass
class MarketPrice(BaseObject):
    tkrList : list
    mktTkrPrices: BaseDict = None

    def __post_init__(self):

        self.mktTkrPrices = getPricesFor(self.tkrList)
        # self.mktTkrPrices.convertContainerToThis(res)
        return

    def getTickerDetails(self,  ticker):
        return self.mktTkrPrices.getValue(ticker)

    def getPrice(self, ticker):
        tickerInfo = self.getTickerDetails(ticker)
        from market.ticker import Ticker
        if isinstance(tickerInfo, Ticker):
            lastP = tickerInfo.getPrice()
            return lastP
        return None

        # return self.getTickerDetails(ticker).getPrice()
    #
    # def print(self):
    #     if isinstance(self.mktTkrPrices, BaseDict):
    #         for

if __name__ == '__main__':
    tkrL = ['DUFRY', 'AAPL', 'MSFT', 'APPL', 'CSCO', 'FAGIX', 'SRNE']
    # lst = BaseDict()
    # lst.convertContainerToThis(tkrL)
    r = get_market_price('AAPL')
    mktP = MarketPrice(tkrL)

    for t in tkrL:
        print({t:mktP.getPrice(t)})

    print (getPricesFor('AAPL'))
