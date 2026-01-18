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
