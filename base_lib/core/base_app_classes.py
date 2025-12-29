import inspect
import os.path
import math

from dataclasses import dataclass, field, fields

from pprint import pprint as print
import pandas as pd

# from base_classes import BaseObjectItem, BaseDate
#
# OPEN = 'O'
# FILLED = 'F'
# @dataclass
# class BaseCustomStatus(BaseObjectItem):
#     def __post_init__(self):
#         self.origStatus = self.getBase()
#         tmp = str(self.getBase())[0]
#         valid_status = {'O', 'F', 'V', 'P', 'B', 'S'}
#         if tmp not in valid_status:
#             err = f"Error to set up status {valid_status} - found - {tmp} -"
#             raise Exception(err)
#         self.setBase(tmp)
#         return
#     def getOrigStatus(self):
#         if isinstance(self.origStatus, str):
#             return self.origStatus
#         if isinstance(self.origStatus, BaseObject):
#             return self.origStatus.getBase()
#         return None
#     def isStatus(self, status):
#         return self.getBase() == status
#     def isOpen(self):
#         return self.isStatus(OPEN)
#     def isFilled(self):
#         return self.isStatus(FILLED)
#
#     def __str__(self):
#         base_str = "{:>3}".format(self.getBase())
#         # print(sym)
#         return base_str
#
# @dataclass
# class BaseBuySell(BaseObjectItem):
#     def __post_init__(self):
#         # tmp = str(self.getBase())[0]
#
#         tmp = self.getBase()
#         if isinstance(tmp, str):
#             tmp = tmp.replace("YOU ", "")
#         tmp1 = tmp[0]
#         if tmp1 not in {'B', 'S', 'E', 'D', 'I', 'R'}:
#             raise Exception("Error to set up BaseBuySell")
#         self.setBase(tmp1)
#         return
#     def isBS(self, bs):
#         return self.getBase() == bs
#     def isBuy(self):
#         return self.isBS('B')
#
#     def isSell(self):
#         return self.isBS('S')
#
#     def __str__(self):
#         base_str = "{}".format(self.getBase())
#         # print(sym)
#         return base_str

from pandas.tseries.holiday import USFederalHolidayCalendar
def getNoOfBusinessDaysFromDate(fromDate, todate=None):
    if todate is None:
        todate = pd.Timestamp.today().date()

    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=fromDate, end=todate)
    return len(pd.bdate_range(start=fromDate, end=todate,  freq='C', holidays=holidays))


if __name__ == "__main__":
    print("This is base_app_classes.py")
    # Define two dates
    start_date = '2025-05-15'
    end_date = '2025-05-21'

    # Get the business days between the two dates
    business_days = getNoOfBusinessDaysFromDate(fromDate=start_date) #, todate=end_date)

    # Print the result
    print(f"Number of business days: between {start_date} and {end_date}: {business_days}")
