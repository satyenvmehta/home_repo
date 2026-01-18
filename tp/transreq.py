Debug_sym = "BLUE"
import common_include as C

@C.dataclass
class TransRequest(C.BaseObject):
    Symbol: BaseTradeSymbol = None
    bs: C.BaseString = None

    reccomnd: C.BaseString = None

    PerGnL: C.BaseFloat = None
    ActToSell : C.BaseString = None
    Yield : C.BaseFloat = None
    price : C.BaseString = None
    lastP : BaseTradePrice = None


from TradeUtil import BaseTrades
@C.dataclass
class TransRequests(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        return

header = ["Symbol", "BS", "Recommend", "PerGnL",
          "ActToSell",  "Yield",
           "Price", "lastP"]

def append(b, t):
    bdf, bsm =  t.toDF(sep='|', header=header)
    b.export_df = pd.concat([b.export_df, bdf], ignore_index=True)
    return b

def tr():
    b = TransRequests()
    tr = TransRequest('t', 't', 'bs', 10, 'abc', 3, '3', 5)
    append(b, tr)
    tr1 = TransRequest('t', 't', 'bs', 10, 'abc', 3, '3', 5)
    append(b, tr1)

    print(b.export_df)

    print("Done..")

if __name__ == '__main__':
    tr()


