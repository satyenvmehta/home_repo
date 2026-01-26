import common_include as C

def isEFT(tkr):
    if tkr in C.ETF:
        return True
    return False
def ignore_ticker(tkr):
    if tkr[0].isdigit() or tkr.startswith("adj ") or tkr in C.MFList or tkr in C.ExceptionTicker:
        return True
    if len(tkr) > 5:
        return True
    if isEFT(tkr):
        return True
    return False
def _validate_ticker(tkr):
    if ignore_ticker(tkr):
        return False
    return True

if __name__ == '__main__':
    tkr = 'G637AM'
    print(_validate_ticker(tkr))