import common_include as C

OPEN = 'O'
FILLED = 'F'
@C.dataclass
class BaseCustomStatus(C.BaseObjectItem):
    def __post_init__(self):
        self.origStatus = self.getBase()
        tmp = str(self.getBase())[0]
        valid_status = {OPEN, FILLED, 'V', 'P', 'B', 'S'}
        if tmp not in valid_status:
            err = f"Error to set up status {valid_status} - found - {tmp} -"
            raise Exception(err)
        self.setBase(tmp)
        return
    def getOrigStatus(self):
        if isinstance(self.origStatus, str):
            return self.origStatus
        if isinstance(self.origStatus, C.BaseObject):
            return self.origStatus.getBase()
        return None
    def isStatus(self, status):
        return self.getBase() == status
    def isOpen(self):
        return self.isStatus(OPEN)
    def isFilled(self):
        return self.isStatus(FILLED)

    def __str__(self):
        base_str = "{:>3}".format(self.getBase())
        # print(sym)
        return base_str

BUY = 'B'
SELL = 'S'

@C.dataclass
class BaseBuySell(C.BaseObjectItem):
    def __post_init__(self):
        # tmp = str(self.getBase())[0]

        tmp = self.getBase()
        if isinstance(tmp, str):
            tmp = tmp.replace("YOU ", "")   # This is to replace "You Bought/You Sold " to B/S
        tmp1 = tmp[0]
        if tmp1 not in {BUY, SELL, 'E', 'D', 'I', 'R'}:
            raise Exception("Error to set up BaseBuySell")
        self.setBase(tmp1)
        return
    def isBS(self, bs):
        return self.getBase() == bs
    def isBuy(self):
        return self.isBS(BUY)

    def isSell(self):
        return self.isBS(SELL)

    def __str__(self):
        base_str = "{}".format(self.getBase())
        # print(sym)
        return base_str


def isMFSym(sym):
    # if self.getBase() == 'ILTB':
    #     return True
    if len(sym) == 5 and str(sym).startswith("F"):
        # print(self.getBase())
        return True
    return False

ExceptionTicker = [
'L4135L100','SPAXX','SRNEQ','TSPH', 'SCLX', 'SRNE', "FZDXX", "MODVQ"
]
MutFundList = [
    'FAGIX', 'FBIOX', 'FDCPX', 'FDRXX', 'FHIFX', 'FHKCX', 'FIDSX', 'FIEUX', 'FNBGX', 'FOCPX', 'FPHAX', 'FRESX',
     'FSAGX', 'FSAVX', 'FSCHX', 'FSCSX', 'FSDAX', 'FSDPX', 'FSELX', 'FSENX', 'FSHCX', 'FSLBX', 'FSLEX', 'FSPHX',
     'FSPTX', 'FSRBX', 'FSRFX', 'FUMBX', 'FWRLX', 'FWWFX', ]

import re


def is_option_symbol(symbol):
    # Pattern: Look for digits, then 'C' or 'P', then more digits
    pattern = r"\d+[CP]\d+"
    if re.search(pattern, symbol):
        return True
    return False


import re


def robust_option_parser(symbol):
    # Regex Breakdown:
    # ^([A-Z0-9.]+) -> Group 1: Ticker. Allows letters, numbers, and dots (e.g., BRK.B)
    # \.?           -> Optional: Handles an extra dot between ticker and date
    # (\d{6})       -> Group 2: The Date (YYMMDD)
    # ([CP])        -> Group 3: 'C' or 'P'
    # (\d+)         -> Group 4: The Strike Price (variable length)

    pattern = r"^([A-Z0-9.]+)\.?(\d{6})([CP])(\d+)$"
    pattern = r"^([A-Z0-9.]+)(\d{6})([CP])([\d.]+)"

    # Use IGNORECASE in case symbols are lowercase
    match = re.match(pattern, symbol, re.IGNORECASE)

    if match:
        ticker = match.group(1).upper()
        date_str = match.group(2)
        type_char = match.group(3).upper()
        strike_val = match.group(4)

        # Determine Strike Price
        # Rule of thumb: if it's 8 digits, it's the OSI standard (/1000)
        # If it's short, it's usually the direct price.
        if "." in strike_val:
            strike_price = float(strike_val)
        elif len(strike_val) == 8:
            strike_price = float(strike_val) / 1000
        else:
            strike_price = float(strike_val)

        return {
            "Ticker": ticker,
            "Type": "Call" if type_char == 'C' else "Put",
            "Expiry": f"{date_str[2:4]}/{date_str[4:]}/20{date_str[:2]}",
            "Strike": strike_price
        }

    return "Not an Option Symbol"

@C.dataclass
class BaseTradeSymbol(C.BaseObjectItem):
    def __post_init__(self):
        return
    def __str__(self):
        base_str = "{:>15}".format(self.getBase())
        return base_str
    def isMF(self):
        return isMFSym(self.getBase())
        # if len(self.getBase()) == 5 and str(self.getBase()).startswith("F"):
        #     return True
        # return False
    def isOpt(self):
        return is_option_symbol(self.getBase())
    def getOptSymbol(self):
        if self.isOpt():
            return BaseOptionSymbol(self.getBase())
        return None
    def __eq__(self, other):
        if isinstance(other, C.BaseObject):
            if self.getBase() == other.getBase():
                return True
        else:
            if isinstance(other, str):
                if self.getBase() == other:
                    return True
        return False

    def validate(self):
        tkr = self.getBase()
        if tkr in ExceptionTicker:
            return False
        if tkr in MutFundList:
            return False
        if tkr.startswith('adj'):
            return False
        return True

@C.dataclass
class BaseTradePrice(C.BaseMoney):
    def __post_init__(self):
        super().__post_init__()
        return
    def __str__(self):
        return super().__str__()

    # format_str = '$#,##0.00' #"${:,.2f}"

@C.dataclass
class BaseOptionSymbol(C.BaseObjectItem):
    def __post_init__(self):
        self.tkr = C.BaseString("")
        self.exp = C.BaseDate("01/01/2000")
        self.strike = C.BaseFloat(0.0)
        self.opt_type = C.BaseString("C")
        self.parse()
        return
    def getDesc(self):
        return f"{self.tkr} {self.exp} {self.opt_type} {self.strike}"
    def parse(self):
        result = robust_option_parser(self.getBase())
        if isinstance(result, dict):
            self.tkr = C.BaseString(result["Ticker"])
            self.exp = C.BaseDate(result["Expiry"])
            self.strike = C.BaseFloat(result["Strike"])
            self.opt_type = C.BaseString(result["Type"])
        return
    def get_tkr(self):
        return self.tkr
    def get_exp(self):
        return self.exp
    def get_strike(self):
        return self.strike
    def get_type(self):
        return self.opt_type

    def __str__(self):
        return self.getBase()

if __name__ == "__main__":
    for sym in ["QUBT260206C12.5", "SPY230616P00420000", "BRK.B250620C00150000", "AAPL.250620C150", "TSLA241220P200", "QUBT260206C12.5"]:
        print("Sym ... " , sym)
        o = BaseOptionSymbol(sym)
        print(o.get_tkr(), o.get_exp(), o.get_strike(), o.get_type())
    # o = BaseOptionSymbol("SPY230616P00420000")
    # print(o)
    # print(o.get_tkr(), o.get_exp(), o.get_strike(), o.get_type())