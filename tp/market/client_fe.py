import common_include as C
from tp.market.client import getPricesFor

from tp.market.get_price import get_market_price


@C.dataclass
class MarketPrice(C.BaseObject):
    tkrList : list
    mktTkrPrices: C.BaseDict = None

    def __post_init__(self):

        self.mktTkrPrices = getPricesFor(self.tkrList)
        # self.mktTkrPrices.convertContainerToThis(res)
        return

    def getTickerDetails(self,  ticker):
        return self.mktTkrPrices.getValue(ticker)

    def getPrice(self, ticker):
        tickerInfo = self.getTickerDetails(ticker)
        from tp.lib.ticker import Ticker
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
    r = get_market_price('AAPL')
    mktP = MarketPrice(tkrL)

    for t in tkrL:
        print({t:mktP.getPrice(t)})

    print (getPricesFor('AAPL'))
