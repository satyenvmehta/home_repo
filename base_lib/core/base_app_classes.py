import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
def getNoOfBusinessDaysFromDate(fromDate, toDate=None):
    if toDate is None:
        toDate = pd.Timestamp.today().date()
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=fromDate, end=toDate)
    return len(pd.bdate_range(start=fromDate, end=toDate,  freq='C', holidays=holidays))

def getDeltaPercentage(p1, p2):
    deltaP = 100 * (p1 - p2) / p1
    return deltaP

def getDaysFromDate(fromDate, todate=None):
    if todate is None:
        todate = pd.Timestamp.today().date()
    delta = todate - fromDate
    return delta.days
def getDaysFromToday(date):
    today = pd.Timestamp.today().date()
    delta = date - today
    return delta.days
def getChangePercent(price1, price2):
    change = (price2 - price1) / price1 * 100
    return round(change, 2)
def getChangePercentFromList(prices):
    if len(prices) < 2:
        return 0
    return getChangePercent(prices[-2], prices[-1])
if __name__ == "__main__":
    print("This is base_app_classes.py")
    # Define two dates
    start_date = '2025-05-15'
    end_date = '2025-05-21'

    # Get the business days between the two dates
    business_days = getNoOfBusinessDaysFromDate(fromDate=start_date) #, todate=end_date)
    # Print the result
    print(f"Number of business days: between {start_date} and {end_date}: {business_days}")
