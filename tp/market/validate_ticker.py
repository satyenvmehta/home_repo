from base_lib.core.common_include import MFList

ExceptionTicker = [
'L4135L100','SPAXX','SRNEQ','TSPH', 'SCLX', 'SRNE', 'SPHIX',
]

ETF = ['ARKK', 'ILTB', ]
def isEFT(tkr):
    if tkr in ETF:
        return True
    return False
def ignore_ticker(tkr):
    if tkr[0].isdigit() or tkr.startswith("adj ") or tkr in MFList or tkr in ExceptionTicker:
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