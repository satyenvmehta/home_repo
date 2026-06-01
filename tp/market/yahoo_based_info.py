# import os
# from dataclasses import dataclass
# from datetime import datetime
from pprint import pprint
import yfinance as yf

from base_lib.core.base_classes import sleep_sec
from tp.lib.mrkt_include import DEBUG_TICKERS


def getHistoricalData(tickers):
    if not isinstance(tickers, list):
        return False
    print("downloading data for ", tickers)
    print("Total tickers ....",  len(tickers))
    data = yf.download(tickers, period="30d", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    print("download complete")
    return data

def _getTickerObjYF(tkr_in):
    try:
        tkr = yf.Ticker(tkr_in)
        info = tkr.info
        no_days = 5
        hist_df = tkr.history(period=f"{no_days + 5}d")
        return tkr, hist_df
    except:
        sleep_sec(1)
        return None, None

# def _tkr_hist(tkr, period='30d', interval='1d'):
#     tkr_o = _getTickerObjYF(tkr)
#     if not tkr_o:
#         return None
#     # data = tkr_o.history(period=period, interval=interval)
#     no_days = 5
#     df = tkr_o.history(period=f"{no_days + 5}d")
#     return df

def _getTickerObj(sym):
    tries = 0
    tkr = None
    while tries < 3:
        tries += 1
        tkr, hist_df = _getTickerObjYF(sym)
        if tkr:
            break
    if not tkr:
        print(f"Error getting ticker object for {sym}")
        return None, None

    return tkr.info, hist_df

if __name__ == '__main__':
    print("test")
    curr, hist = _getTickerObj('AAPL')
    for tkr in DEBUG_TICKERS:
        curr, hist = _getTickerObj(tkr)
        if curr is None:
            print(tkr, "None returned")
            continue
        print(tkr, '..PE and Sector ====>', curr.get( 'trailingPE', 'N/A'), curr.get('sector', 'N/A'))
        print(hist)
    pprint(getHistoricalData(['AAPL', 'AMZN', 'MSFT', 'GOOG']))



'''
Market data info has following attributes with example as follows:
pprint(info)
{'52WeekChange': 0.5618887,
 'SandP52WeekChange': 0.283121,
 'address1': 'One Apple Park Way',
 'allTimeHigh': 305.54,
 'allTimeLow': 0.049107,
 'ask': 311.0,
 'askSize': 1,
 'auditRisk': 2,
 'averageAnalystRating': '2.0 - Buy',
 'averageDailyVolume10Day': 44141720,
 'averageDailyVolume3Month': 43669777,
 'averageVolume': 43669777,
 'averageVolume10days': 44141720,
 'beta': 1.065,
 'bid': 309.23,
 'bidSize': 1,
 'boardRisk': 1,
 'bookValue': 7.26,
 'city': 'Cupertino',
 'companyOfficers': [{'age': 64,
                      'exercisedValue': 0,
                      'fiscalYear': 2025,
                      'maxAge': 1,
                      'name': 'Mr. Timothy D. Cook',
                      'title': 'CEO & Director',
                      'totalPay': 16759518,
                      'unexercisedValue': 0,
                      'yearBorn': 1961},
 'compensationAsOfEpochDate': 1767139200,
 'compensationRisk': 7,
 'corporateActions': [],
 'country': 'United States',
 'cryptoTradeable': False,
 'currency': 'USD',
 'currentPrice': 309.315,
 'currentRatio': 1.07,
 'customPriceAlertConfidence': 'HIGH',
 'dateShortInterest': 1777507200,
 'dayHigh': 311.4,
 'dayLow': 305.85,
 'debtToEquity': 79.548,
 'displayName': 'Apple',
 'dividendDate': 1778716800,
 'dividendRate': 1.08,
 'dividendYield': 0.35,
 'earningsCallTimestampEnd': 1777582800,
 'earningsCallTimestampStart': 1777582800,
 'earningsGrowth': 0.218,
 'earningsQuarterlyGrowth': 0.194,
 'earningsTimestamp': 1777579200,
 'earningsTimestampEnd': 1785441600,
 'earningsTimestampStart': 1785441600,
 'ebitda': 159975997440,
 'ebitdaMargins': 0.35437,
 'enterpriseToEbitda': 28.102,
 'enterpriseToRevenue': 9.959,
 'enterpriseValue': 4495700918272,
 'epsCurrentYear': 8.74834,
 'epsForward': 9.60383,
 'epsTrailingTwelveMonths': 8.27,
 'esgPopulated': False,
 'exDividendDate': 1778457600,
 'exchange': 'NMS',
 'exchangeDataDelayedBy': 0,
 'exchangeTimezoneName': 'America/New_York',
 'exchangeTimezoneShortName': 'EDT',
 'executiveTeam': [],
 'fiftyDayAverage': 269.4906,
 'fiftyDayAverageChange': 39.8244,
 'fiftyDayAverageChangePercent': 0.14777659,
 'fiftyTwoWeekChangePercent': 56.18887,
 'fiftyTwoWeekHigh': 311.4,
 'fiftyTwoWeekHighChange': -2.0849915,
 'fiftyTwoWeekHighChangePercent': -0.006695541,
 'fiftyTwoWeekLow': 193.46,
 'fiftyTwoWeekLowChange': 115.854996,
 'fiftyTwoWeekLowChangePercent': 0.5988576,
 'fiftyTwoWeekRange': '193.46 - 311.4',
 'financialCurrency': 'USD',
 'firstTradeDateMilliseconds': 345479400000,
 'fiveYearAvgDividendYield': 0.51,
 'floatShares': 14662387495,
 'forwardEps': 9.60383,
 'forwardPE': 32.207462,
 'freeCashflow': 101090746368,
 'fullExchangeName': 'NasdaqGS',
 'fullTimeEmployees': 166000,
 'gmtOffSetMilliseconds': -14400000,
 'governanceEpochDate': 1777593600,
 'grossMargins': 0.47862,
 'grossProfits': 216070995968,
 'hasPrePostMarketData': True,
 'heldPercentInsiders': 0.01633,
 'heldPercentInstitutions': 0.65963,
 'impliedSharesOutstanding': 14687356000,
 'industry': 'Consumer Electronics',
 'industryDisp': 'Consumer Electronics',
 'industryKey': 'consumer-electronics',
 'irWebsite': 'http://investor.apple.com/',
 'isEarningsDateEstimate': True,
 'language': 'en-US',
 'lastDividendDate': 1778457600,
 'lastDividendValue': 0.27,
 'lastFiscalYearEnd': 1758931200,
 'lastSplitDate': 1598832000,
 'lastSplitFactor': '4:1',
 'longBusinessSummary': 'Apple Inc. designs, manufactures, and markets '
                        ........
                        'Cupertino, California.',
 'longName': 'Apple Inc.',
 'market': 'us_market',
 'marketCap': 4543019483136,
 'marketState': 'REGULAR',
 'maxAge': 86400,
 'messageBoardId': 'finmb_24937',
 'mostRecentQuarter': 1774656000,
 'netIncomeToCommon': 122575003648,
 'nextFiscalYearEnd': 1790467200,
 'nonDilutedMarketCap': 4479496706440,
 'numberOfAnalystOpinions': 43,
 'open': 306.06,
 'operatingCashflow': 140222005248,
 'operatingMargins': 0.32275,
 'overallRisk': 1,
 'payoutRatio': 0.1259,
 'pegRatio': 2.63,
 'phone': '(408) 996-1010',
 'previousClose': 304.99,
 'priceEpsCurrentYear': 35.356995,
 'priceHint': 2,
 'priceToBook': 42.60537,
 'priceToSalesTrailing12Months': 10.063351,
 'profitMargins': 0.27152002,
 'quickRatio': 0.906,
 'quoteSourceName': 'Nasdaq Real Time Price',
 'quoteType': 'EQUITY',
 'recommendationKey': 'buy',
 'recommendationMean': 1.95833,
 'region': 'US',
 'regularMarketChange': 4.325012,
 'regularMarketChangePercent': 1.4180833,
 'regularMarketDayHigh': 311.4,
 'regularMarketDayLow': 305.85,
 'regularMarketDayRange': '305.85 - 311.4',
 'regularMarketOpen': 306.06,
 'regularMarketPreviousClose': 304.99,
 'regularMarketPrice': 309.315,
 'regularMarketTime': 1779472903,
 'regularMarketVolume': 27041526,
 'returnOnAssets': 0.26229,
 'returnOnEquity': 1.4147099,
 'revenueGrowth': 0.166,
 'revenuePerShare': 30.534,
 'sector': 'Technology',
 'sectorDisp': 'Technology',
 'sectorKey': 'technology',
 'shareHolderRightsRisk': 1,
 'sharesOutstanding': 14687356000,
 'sharesPercentSharesOut': 0.0092,
 'sharesShort': 134675274,
 'sharesShortPreviousMonthDate': 1774915200,
 'sharesShortPriorMonth': 126771284,
 'shortName': 'Apple Inc.',
 'shortPercentOfFloat': 0.0092,
 'shortRatio': 3.11,
 'sourceInterval': 15,
 'state': 'CA',
 'symbol': 'AAPL',
 'targetHighPrice': 400.0,
 'targetLowPrice': 215.0,
 'targetMeanPrice': 308.6465,
 'targetMedianPrice': 310.0,
 'totalCash': 68507000832,
 'totalCashPerShare': 4.664,
 'totalDebt': 84710998016,
 'totalRevenue': 451442016256,
 'tradeable': False,
 'trailingAnnualDividendRate': 1.04,
 'trailingAnnualDividendYield': 0.003409948,
 'trailingEps': 8.27,
 'trailingPE': 37.402054,
 'trailingPegRatio': 2.6539,
 'triggerable': True,
 'twoHundredDayAverage': 261.0716,
 'twoHundredDayAverageChange': 48.24341,
 'twoHundredDayAverageChangePercent': 0.18478996,
 'typeDisp': 'Equity',
 'volume': 27041526,
 'website': 'https://www.apple.com',
 'zip': '95014'}

'''
