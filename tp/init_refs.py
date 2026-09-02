import common_include as C

from tp.all_history import Historys
from tp.order import Orders
from tp.position import Positions

hist_vals = Historys()
pos_vals = Positions()
ords_vals = Orders()


def appendToTkrSet(ts, tkr):
    if tkr.startswith("adj "):
        return
    if tkr[0].isdigit():
        return
    if tkr in C.ExceptionTicker:
        return
    ts.append(tkr)
    return

def create_ticker_list():
    uniqPosList = pos_vals.getUniqueSymbols()
    uords_tkr = ords_vals.getUniqueSymbols()
    uhist_tkr = hist_vals.getUniqueSymbols()
    tksSet = C.BaseSet()
    # all_tickers = TickersSet()
    import itertools
    for tkr in itertools.chain(uhist_tkr, uords_tkr):
        appendToTkrSet(tksSet, tkr)
    for tkr in uniqPosList:
        appendToTkrSet(tksSet, tkr)
    tksSet.sort(key=None, reverse=False)
    # tksSet.saveToCSV(C.ticker_file, header=["Symbol"])
    return tksSet


def initRefData():
    if not hist_vals or not pos_vals or not ords_vals:
        return None, None, None
    C.TickersSet = create_ticker_list()
    C.NoOfTickers = C.TickersSet.size()
    print("No. of unique tickers: " + str(C.NoOfTickers))
    return hist_vals, pos_vals, ords_vals

if __name__ == '__main__':
    hist_vals, pos_vals, ords_vals = initRefData()
    if isinstance(hist_vals, Historys):
        print("hist_vals is Historys")
    if isinstance(pos_vals, Positions):
        print("pos_vals is Positions")
    if isinstance(ords_vals, Orders):
        print("ords_vals is Orders")
