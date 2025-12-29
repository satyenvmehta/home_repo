from base_lib.core.base_container_classes import BaseSet
from base_lib.core.common_include import *
from base_lib.core.base_classes import BaseString, BaseFloat, BaseObject


@dataclass
class Ticker(BaseObject):
    symbol : BaseString
    price : BaseFloat

    # price_change
    # year_high
    # year_low
    # day_high
    # day_low
    # sector

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        self.price = self.price.round(2)
        return


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

@dataclass
class TickersSet(BaseSet):
    tickers : list[Ticker]

    def __post_init__(self):
        self.tickers = sorted(list(set(self.tickers)))
        return

    def __str__(self):
        return "\n".join([str(ticker) for ticker in self.tickers])
    def __repr__(self):
        return "\n".join([str(ticker) for ticker in self.tickers])
    def __len__(self):
        return len(self.tickers)
    def __getitem__(self, index):
        return self.tickers[index]
    def __iter__(self):
        return iter(self.tickers)
    def __contains__(self, item):
        return item in self.tickers
    def __eq__(self, other):
        return self.tickers == other.tickers
    def __hash__(self):
        return hash(tuple(self.tickers))
    def __lt__(self, other):
        return self.tickers < other.tickers
    def __gt__(self, other):
        return self.tickers > other.tickers
    def __le__(self, other):
        return self.tickers <= other.tickers
    def __ge__(self, other):
        return self.tickers >= other.tickers

    def add(self, ticker):
        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self.tickers = sorted(self.tickers)
        return

    def remove(self, ticker):
        if ticker in self.tickers:
            self.tickers.remove(ticker)
        return

    def update(self, tickers):
        for ticker in tickers:
            self.add(ticker)
        return

    def filter(self, filter_func):
        return TickersSet([ticker for ticker in self.tickers if filter_func(ticker)])

