import common_include as C
from TradeUtil import BaseTrades

@C.dataclass
class StockScreener(C.BaseObject):
    """
    A class representing a stock screener.

    Attributes:
        screener_name (str): The name of the screener.
        screener_id (str): The unique identifier of the screener.
        screener_url (str): The URL of the screener.
        screener_description (str): The description of the screener.
        screener_criteria (str): The criteria used to filter stocks in the screener.
        screener_stocks (list): A list of stocks included in the screener.
    """

    screener_name: str
    screener_id: str
    screener_url: str
    screener_description: str
    screener_criteria: str
    screener_stocks: list

    def __init__(self, screener_name, screener_id, screener_url, screener_description, screener_criteria, screener_stocks):
        """
        Initializes a StockScreener object.

        Args:
            screener_name (str): The name of the screener.
            screener_id (str): The unique identifier of the screener.
            screener_url (str): The URL of the screener.
            screener_description (str): The description of the screener.
            screener_criteria (str): The criteria used to filter stocks in the screener.
            screener_stocks (list): A list of stocks included in the screener.
        """
        self.screener_name = screener_name
        self.screener_id = screener_id
        self.screener_url = screener_url
        self.screener_description = screener_description
        self.screener_criteria = screener_criteria
        self.screener_stocks = screener_stocks

    def __repr__(self):
        """
        Returns a string representation of the StockScreener object.

        Returns:
            str: A string representation of the StockScreener object.
        """
        return f'StockScreener({self.screener_name}, {self.screener_id}, {self.screener_url}, {self.screener_description}, {self.screener_criteria}, {self.screener_stocks})'


@C.dataclass
class StockFundamentals(C.BaseObject):
    """
    A class representing stock fundamentals.

    Attributes:
        Symbol (BaseTradeSymbol): The ticker symbol of the stock.
        Sector
    """
    Symbol: C.BaseTradeSymbol = None
    Sector:C.BaseString = None
    BVPS: C.BasePrice = None
    Growth: C.BasePrice = None

    @classmethod
    def from_dict(cls, data_dict):
        """
        Creates a StockFundamentals object from a dictionary.

        Args:
            data_dict (dict): A dictionary containing the stock fundamentals data.

        Returns:
            StockFundamentals: A StockFundamentals object.
        """
        return cls(
            Symbol=data_dict['Symbol'],
            Sector=data_dict['Sector'],
            BVPS=data_dict['BVPS'],
            Growth=data_dict['Growth']
        )

class StocksFundamentals(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        # sort_by = lambda x: x.Last
        # self.presetTrades(sort_by=sort_by, reverese=False)
        # self.extra_columns = ['Ext Hrs Last', '% Ext Hrs Chg']
        self.cls = StockFundamentals
        self.uniqueCols = ['Symbol']
        self.readFile(self.cls, self.uniqueCols, header_lines=3, datafile=C.stock_fundamentals_file)
        return
    def printValues(self):
        for item in self.getBase():
            print(item)
        return

    def getInfoForSymbol(self, sym):
        if isinstance(sym, C.BaseObject):
            sym = sym.getBase()
        obj = self.getCurrentObj(sym)
        if isinstance(obj, StockFundamentals):
            return obj
        return self.getBase().getInfo(sym)


@C.dataclass
class StockFilterAttributes(C.BaseObject):
    Symbol: C.BaseTradeSymbol = None
    today_open : C.BasePrice = None
    intraday_range_per: C.BasePrice = None
    open_close_gap_per: C.BasePrice = None
    overnight_gap: C.BasePrice = None
    today_high: C.BasePrice = None
    today_low: C.BasePrice = None
    close_today: C.BasePrice = None
    rsi: C.BasePrice = None
    bs_indicator:C.BaseString = None
    bd_advise:C.BaseString = None
    pos: C.BaseInt = None


    def init_from_df(self, symbol, df, rsi, bs_indicator, bd_advise, pos):
        """
        Initializes the StockFilterAttributes object from a pandas DataFrame.

        Args:
            symbol: Ticker Symbol
            df (pandas.DataFrame): The DataFrame containing the stock data.
            :param bd_advise:
            :param bs_indicator:
            :param df:
            :param symbol:
            :param rsi: Relative Strength Index

        """
        self.Symbol = C.BaseTradeSymbol(symbol)
        self.today_open = C.BasePrice((df['Open'].iloc[-1]))
        self.today_high = C.BasePrice((df['High'].iloc[-1]))
        self.today_low = C.BasePrice((df['Low'].iloc[-1]))
        prev_close = C.BasePrice((df['Close'].iloc[-2]))
        self.close_today = C.BasePrice((df['Close'].iloc[-1]))
        self.overnight_gap = self.today_open - prev_close

        self.intraday_range_per = (self.today_high - self.today_low) * 100.0 / self.today_open
        self.intraday_range_per = C.BasePrice(self.intraday_range_per.getBase())
        self.open_close_gap_per = (self.close_today - self.today_open) * 100.0 / self.today_open
        self.open_close_gap_per = C.BasePrice(self.open_close_gap_per.getBase())
        self.intraday_range = (self.today_high - self.today_low)
        self.open_close_gap = (self.close_today - self.today_open)
        self.rsi = rsi
        self.bs_indicator = bs_indicator
        self.bd_advise = bd_advise
        self.pos = pos
        return
    def __repr__(self):
        """
        Returns a string representation of the StockFilterAttributes object.

        Returns:
            str: A string representation of the StockFilterAttributes object.
        """
        return f'StockFilterAttributes({self.Symbol}, {self.today_open}, {self.intraday_range_per}, {self.open_close_gap_per}, {self.overnight_gap}, {self.today_high}, {self.today_low}, {self.close_today}, {self.rsi}, {self.bs_indicator}, {self.bd_advise})'


if __name__ == '__main__':
    b = StocksFundamentals()
    b.printValues()
