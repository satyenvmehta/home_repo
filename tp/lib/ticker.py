from base_lib.core.common_include import *
from base_lib.core.base_classes import BaseString, BaseFloat, BasePrice

ExceptionTicker = [
'L4135L100','SPAXX','SRNEQ','TSPH', 'SCLX', 'SRNE', 'SPHIX',
]

ETF = ['ARKK', 'ILTB', ]

@dataclass
class Ticker:
    symbol : BaseString
    price : BasePrice

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        return

    def getPrice(self):
        return self.price.getBase()

    def isPennyStock(self):
        if self.price is None:
            return False
        return self.price.isPennyStock()

    def isZeroPrice(self):
        if self.price is None:
            return True
        return self.price.isZero()
    def isETF(self):
        if self.symbol in ETF:
            return True
        return False
    def isMF(self):
        if self.symbol in MFList:
            return True
        return False
    def isExceptionTicker(self):
        if self.symbol in ExceptionTicker:
            return True
        return False
    def isValidTicker(self):
        tkr = self.symbol.getBase()
        if tkr[0].isdigit() or tkr.startswith("adj ") or tkr in MFList:
            return False
        if tkr in ExceptionTicker:
            return False
        if len(tkr) > 6:
            return False
        return True


    # price_change
    # year_high
    # year_low
    # day_high
    # day_low
    # sector

    def __str__(self):
        return f"{self.symbol} {self.price}"
    def __repr__(self):
        return f"{self.symbol} {self.price}"
    def __eq__(self, other):
        return self.symbol == other.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __lt__(self, other):
        return self.price < other.price
    def __gt__(self, other):
        return self.price > other.price
    def __le__(self, other):
        return self.price <= other.price
    def __ge__(self, other):
        return self.price >= other.price

if __name__ == "__main__":
    t = Ticker("aapl", BasePrice(100.255))
    print(t.getPrice())
    print(t.isPennyStock())
    print(t.isZeroPrice())
    print(t.getPrice())
