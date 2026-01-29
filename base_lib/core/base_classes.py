import inspect
import math

from dataclasses import dataclass, field, fields
from pprint import pprint

import pandas as pd
from pandas import DataFrame
from datetime import  datetime 

def getTodayYYYYMMDD():
    # print({"DEBUG:" : type(dt) } )
    dt1 = datetime.today().strftime('%Y%m%d') 
    return dt1

from base_lib.core.sys_utils import Today

@dataclass
class Rectangle:
    height: float
    width: float

@dataclass
class Square(Rectangle):
    side: float

    def __post_init__(self):
        super().__init__(self.side, self.side)

@dataclass
class BaseObject:
    # _item : any = None
    def setBase(self, base_val):
        self._item = base_val
        return
    def _init_none(self):
        self.setBase(None)
        return

    def setClassMembers(self):
        self.resetDebug()
        self.setHeader()
        return
    def __post_init__(self):
        self._init_none()
        # self.resetDebug()
        # self.setHeader()
        self.setClassMembers()
        return

    def setHeader(self, head=None):
        self._header = head
        return

    def getBase(self):
        return self._item
    def equals(self, other):
        if isinstance(other, BaseObject):
            other = other.getBase()
        res = self.getBase() == other
        return res

    def isNaN(self):
        from math import isnan
        return isnan(self.getBase())

    def setDebug(self, flag=True):
        self._debug_flag = flag
        return
    def resetDebug(self):
        self.setDebug(False)
        return
    def getDebug(self):
        return self._debug_flag

    def valid_number_value(self):
        if self.getBase() == '--':
            return False
        if str(self.getBase()).upper() == 'NAN':
            return False
        return True
    def remove_commas(self):
        if isinstance(self.getBase(), str):
            self.setBase(self.getBase().replace(",", ""))
        return

    def remove_dollarsign(self):
        if isinstance(self.getBase(), str):
            self.setBase(self.getBase().replace("$", ""))
        return

    def replace_paran_to_neg(self):
        if isinstance(self.getBase(), str):
            self.setBase(self.getBase().replace("(", "-"))
            self.setBase(self.getBase().replace(")", ""))
        return

    def __eq__(self, other):
        if isinstance(other, BaseObject):
            return self.getBase() == other.getBase()
        res = self.getBase() == other
        return res

    def __lt__(self, other):
        return self.getBase() < other.getBase()

    def to_str(self):
        return str(self.getBase())

    def print(self):
        pprint(self)

    def pretty_print_members(self, include_methods=False):
        """Print all members of the class instance in a pretty format."""
        if include_methods:
            # Get all members including methods
            members = inspect.getmembers(self)
            pprint(members)
        else:
            # Print only instance attributes
            pprint(self.__dict__)
        return

    def debug(self, str_val):
        if self.getDebug():
            print(str_val)

    def is_file_locked(self, file_path):
        import psutil
        for proc in psutil.process_iter(['open_files']):
            try:
                for item in proc.info['open_files'] or []:
                    if item.path == file_path:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def is_file_in_use(self, fullFileName):
        return self.is_file_locked(file_path=fullFileName)

    def _saveResults(self, listOfInterest, fileName, altFilename=None):
        workbook = None
        if listOfInterest is None:
            print("Nothing to save")
            return

        fullFileName = fileName

        print("Saving to file " + fullFileName)
        with pd.ExcelWriter(fullFileName, engine='xlsxwriter') as writer:
            sp_formats = {}
            print("Creating sheet ..")
            for item, dobj in listOfInterest.items():
                print("   "+ item)
                df = None
                # from base_classes import BaseInt, BaseCustomStatus, BaseBuySell, BasePercentage
                # from base_classes import BaseObject, BaseObjectItem, BaseString, BaseFloat, BaseMoney
                from base_lib.core.base_container_classes import  BaseReaderWriter
                if isinstance(dobj, BaseReaderWriter):
                    df = dobj.export_class_data_to_df()
                elif isinstance(dobj, DataFrame):
                    df = dobj
                if df is not None:
                    self.remove_extra_columns(df)
                    df.to_excel(writer, sheet_name=item, index=0)
                    if not workbook:
                        workbook = writer.book

                    if isinstance(dobj, BaseReaderWriter):
                        formats = dobj.getClassMembersFormats()

                        for membr, frmt in formats.items():
                            sp_formats[membr] = workbook.add_format(frmt)

                        worksheet = writer.sheets[item]
                        from base_lib.core.excel_utils import fromColName2ColIndex
                        for membr, frmt in formats.items():
                            ci = fromColName2ColIndex(df, membr)
                            ci_ci = ci+":"+ci
                            worksheet.set_column(ci_ci, None, sp_formats[membr])
        return

    def _toListOfDict(self):
        dictVal = list(self.__dict__.items())
        return dictVal

    def getBaseObjectMembers(self):
        # return ['_item', '_debug_flag', '_header' ]
        return ['_debug_flag', '_header']

    def remove_extra_columns(self, df, extra_cols=None):
        all_extra_cols = self.getBaseObjectMembers()
        if extra_cols:
            all_extra_cols = all_extra_cols + extra_cols
        for col_name in all_extra_cols:
            if col_name in df.columns:
                df.drop(col_name, axis=1, inplace=True)
        return

    def getClassMembers(self, cls):
        members = {f.name: f.type for f in fields(cls)}
        # for member, mtype in self._members.items():
        #     if mtype is BaseTradePrice:
        return members
    # def getClassMembers(self):
    #     return self._members

    def getLocalMembers(self):
        user_defined_members = []
        for name, value in self.__dict__.items():
            if not name.startswith('__'):
                user_defined_members.append(name)
        return user_defined_members

    def toListOfDict(self):
        bo = self.getBaseObjectMembers()
        dictVal = self._toListOfDict()
        for bitem in bo:
            for item in dictVal:
                if item[0] == bitem:
                    dictVal.remove(item)
        return dictVal

    def getHeader(self):
        if self._header:
            return self._header
        return self.classMemberHeader()

    def classMemberHeader(self):
        lm = self.toListOfDict()
        header = []
        # self.setHeader()
        for m in lm:
            header.append(m[0])

        self.setHeader(header)
        return header

    def toDF(self, sep=":", header=None):
        res_dict_list = self.toListOfDict()
        if not header:
            header = self.getHeader()
        i = 0
        res_msg = ""  # A result string
        fres = {}
        len_header = len(header)
        if isinstance(res_dict_list, list):
            for val in res_dict_list:
                # print(val)
                # if header[i] == val[0]:
                fres[header[i]] = val[1]
                if not val[1]:
                    disval = ""
                else:
                    disval = val[1]
                res_msg = res_msg + str(disval) + sep
                i = i+1
                if i >= len_header:      # This fixed issue of supplied shorter header
                    break
        bs_df_res = [fres]
        bdf = pd.DataFrame(bs_df_res)
        return bdf, res_msg

    def _postRowRead(self):  # To Support Reading CVS file reading a row and process each row
        pass

    def export_class_data_to_df(self):
        df = DataFrame()
        df = pd.concat([df, self.toDF()[0]], ignore_index=True)
        return df

@dataclass
class BaseObjectItem(BaseObject):
    _item: any

    def __post_init__(self):
        # super().__post_init__()
        self.setClassMembers()
        return

@dataclass
class BaseBool(BaseObjectItem):
    def __post_init__(self):
        self.setBase(bool(self.getBase()))
        return
    def __str__(self):
        return "{:7}".format(self.getBase())

@dataclass
class BaseInt(BaseObjectItem):
    def __post_init__(self):
        self.remove_commas()
        if not self.valid_number_value():
            self.setBase(0)
            return
        self.setBase(int(self.getBase()))
        return
    def __str__(self):
        return "{:7}".format(self.getBase())
    def __add__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return BaseInt(self.getBase() + other)
        return BaseInt(self.getBase() + other)
    def __sub__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return BaseInt(self.getBase() - other)
        return BaseInt(self.getBase() - other)
    def __mul__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return BaseInt(self.getBase() * other)
        return BaseInt(self.getBase() * other)
    def __truediv__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return BaseInt(self.getBase() / other)
        return BaseInt(self.getBase() / other)
    def __eq__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() == other
        return self.getBase() == other
    def __lt__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() < other
        return self.getBase() < other
    def __gt__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() > other
        return self.getBase() > other
    def __le__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() <= other
        return self.getBase() <= other
    def __ge__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() >= other
        return self.getBase() >= other
    def __ne__(self, other):
        if isinstance(other, BaseInt):
            other = other.getBase()
            return self.getBase() != other
        return self.getBase() != other
    format_str = {'num_format': '#,##0'}

@dataclass
class MyInteger(int, BaseObject):  # Assuming OtherClass is defined elsewhere
    def __new__(cls, value):
        # You can implement custom behavior here if needed
        return super().__new__(int, value)

@dataclass
class BaseFloat(BaseObjectItem):
    def __post_init__(self):
        super(BaseFloat, self).__post_init__()
        self.remove_commas()
        self.setPrecs()
        if not self.valid_number_value():
            self.setBase(0)
            return
        try:
            val = self.getBase()
            self.setBase(float(val))
        except:
            print("Invalid float " + str(val))
        return
    def setPrecs(self, pres=2):
        self.pres = pres
        return

    def isPositive(self):
        return self.getBase() > 0
    def isNegative(self):
        return self.getBase() < 0
    def isZero(self):
        return self.getBase() == 0

    def toInt(self):
        return int(round(self.getBase(), 0))
    def getBase(self):
        return super().getBase()
    def setBase(self, val):
        super().setBase(val)
        return

    def roundup(self, n=1):
        mult = 10 ** n
        return math.ceil(self.getBase() * mult) / mult

    def rounddown(self, n=1):
        mult = 10 ** n
        return math.floor(self.getBase() * mult) / mult

    def roundit(self):
        self.setBase(round(self.getBase(), self.pres))
        return self.getBase()

    def zero(self):
        self.setBase(0)
        return
    def isZero(self):
        return self.getBase() == 0

    def isNaN(self):
        return math.isnan(self.getBase())

    def __mul__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
        return BaseFloat(self.getBase() * other)
    def __truediv__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
            return BaseFloat(self.getBase() / other)
        return BaseFloat(self.getBase() / other)
    def __add__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
        return BaseFloat(self.getBase() + other)
    def __sub__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
            return BaseFloat(self.getBase() - other)
        return BaseFloat(self.getBase() - other)
    def __gt__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
            return self.getBase() > other
        return self.getBase() > other
    def __lt__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
            return self.getBase() < other
        return self.getBase() < other
    def __eq__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
        return self.getBase() == other
    def __ne__(self, other):
        if isinstance(other, BaseFloat):
            other = other.getBase()
            return self.getBase() != other
        return

    def __str__(self):
        pres = self.pres
        format_str = "{:10." + str(pres) + "f}"
        return format_str.format(self.getBase())

    format_str =  {'num_format': '#,##0.00'}

@dataclass
class BasePercentage(BaseFloat):
    def __post_init__(self):
        super().__post_init__()
        return
    def __str__(self):
        try:
            res = super().__str__() + "%"
        except:
            print("Error BasePercentage " + str(self.getBase()))
            return "None"
        return res

    format_str =  {'num_format': '0.0%'} #"{:.2%}"

@dataclass
class BaseString(BaseObjectItem):
    def __post_init__(self):
        return

    def isNaN(self):
        nan_s = str(self.getBase())
        return nan_s == 'nan'

    def __str__(self):
        return "{:<10}".format(str(self.getBase()))

    def __eq__(self, other):
        res = self.getBase() == other.getBase()
        return res

@dataclass
class BaseMoney(BaseFloat):
    def __post_init__(self):
        self.remove_dollarsign()
        self.replace_paran_to_neg()
        super().__post_init__()
        self.currency_code = "$"
        return
    def __str__(self):
        try:
            val = "{0}{1:10.2f}".format(self.currency_code, self.getBase())
            return val
        except:
            print("BaseMoney _str_ " + str(self.getBase()))
            return "None"
    format_str = {'num_format': '$#,##0.00'}

@dataclass
class BasePrice(BaseFloat):
    def __post_init__(self):
        super().__post_init__()
        self.setBase(round(self.getBase(), 2))
        return

    def isPennyStock(self, penny=3.0):
        return self.getBase() < penny
        # return self < BasePrice(3.0)
    def __mul__(self, other):
        if isinstance(other, BasePrice):
            other = other.getBase()
        return BasePrice(self.getBase() * other)

@dataclass
class BaseDate(BaseObjectItem):
    def __post_init__(self):
        super().__post_init__()
        self.date_format = '%m/%d/%Y'
        dt = ""
        if self.getBase() == "--":
            self.setBase("01/01/1900")
            # self.item = "01/01/1900"
        dtp = None
        try:
            dtp = datetime.strptime(self.getBase(), self.date_format)
        except:
            print("Incorrect value " + str(self.getBase()))
            return
        finally:
            self.setBase(dtp)
        return

    def getNoDaysFromToday(self):
        try:
            noDays = self.getBase() - BaseDate(Today()).getBase()
        except:
            from datetime import timedelta
            noDays = timedelta(0)
            print("getNoDaysFromToday: Error with " + str(self.getBase()))

        return noDays.days

    def isOlderThan(self, noOfDays):
        noOfDaysFromToday = self.getNoDaysFromToday()
        if noOfDaysFromToday *-1 > noOfDays:
            return True
        return False

    def __str__(self):
        try:
            val = self.getBase().strftime(self.date_format)
        except:
            print("Invalid date " + str(self.getBase()))
            return "01/01/1900"
        return val

    def to_dd_mm_yy(self, other):
        try:
            # Parse the string date into a datetime object
            other_date = datetime.strptime(other, "%m/%d/%Y")
        except ValueError:
            raise ValueError(f"Invalid date format. Expected 'DD/MM/YYYY', got: {other}")
        return other_date
    def __lt__(self, other: str) -> bool:
        """
        Compare if the instance date is less than a given string date.
        :param other: Date in string format (e.g., "02/10/2025").
        :return: True if the instance date is less than the given date.
        """
        if isinstance(other, str):
            other = BaseDate(other)
        # Compare the instance date with the parsed date
        return self.getBase() < other.getBase()
    def __eq__(self, other):
        if isinstance(other, str):
            other = BaseDate(other)
        return self.getBase() == other.getBase()
    def __gt__(self, other: str) -> bool:
        """
        Compare if the instance date is less than a given string date.
        :param other: Date in string format (e.g., "02/10/2025").
        :return: True if the instance date is less than the given date.
        """
        if isinstance(other, str):
            other = BaseDate(other)
        # Compare the instance date with the parsed date
        return self.getBase() > other.getBase()

import logging

class Logger:
    def __init__(self, name: str, log_file: str = "app.log"):
        # Create a custom logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Set the base logging level

        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(log_file)

        # Set log level for handlers
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)

        # Create formatters and add them to handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


@dataclass
class MyObject(BaseObject):
    name: BaseString
    date_field : BaseDate

    def __post_init__(self):
        self.setClassMembers()
        self.date_field = BaseDate(self.date_field)
        return

    def __eq__(self, other):
        # if isinstance(self.name, BaseObject):
        #     thisName = self.name.getBase()
        # else:
        #     thisName = self.name
        if self.name == other:
            return True
        return False

@dataclass
class MyObject2(BaseObject):
    name: BaseString
    date_field : BaseDate


objects = [
    MyObject(BaseString("Object1"), "01/15/2023"),
    MyObject(BaseString("Object2"), "02/10/2024"),
    MyObject(BaseString("Object3"), "09/20/2020"),
    MyObject(BaseString("Object2"), "12/10/2024"),
]

def sort_example():
    sorted_objects = sorted(objects, key=lambda x: x.date_field)

    # Print the sorted list
    for obj in sorted_objects:
        print(obj.name)
        print(obj.date_field)

@dataclass
class cmpdObj(BaseObject):
    ticker:str
    bs : str

def DbgBaseDate():
    a = "11/23/2024"
    b = "04/23/2025"
    a1 = BaseDate(a)
    for dt in [a, b]:
        db = BaseDate(dt)
        print(str(db))
        print(db.getNoDaysFromToday())
        print(db.isOlderThan(90))
    if a1.isOlderThan(90):
        print(True)
    b1 = BaseDate(b)
    if a1 == b:
        print(True)
    else:
        print(False)
    if a1 < b:
        print(True)
    if a1 > b:
        print(True)
    else:
        print(False)
    print(a1.getNoDaysFromToday())
    z = BaseDate(None)
    print(z.getNoDaysFromToday())
    a = "03/20/2020"
    b = "01/20/2021"
    b = "12/01/2020"
    print(BaseDate(a))
    print(str(BaseDate(a)))
    print(getTodayYYYYMMDD())
    return

def DbgBaseFltMnyPerc():
    x = BaseFloat(10.234)
    print(str(x))
    x = BaseMoney(100.226)
    print(str(x))
    x = BasePercentage(10.234)
    print(str(x))

    x = BaseFloat(10.234)
    print(str(x))
    x = BasePercentage(10.234)
    print(str(x))
    x = BaseMoney(10.245)
    print(str(x))

    x = BaseMoney(100.226)
    print(str(x))

    return

@dataclass
class TestStrObj:
    a : BaseString
    def __post_init__(self):
        self.a = BaseString(self.a)
        return

@dataclass
class MyDate(BaseObject):
    date_field : BaseDate
    def __post_init__(self):
        self.date_field = BaseDate(self.date_field)
        return

def DbgBasics():
    DbgBaseFltMnyPerc()
    d = MyDate('03/03/2020')
    x = TestStrObj('AA')

    x = int(5.4)
    print(x)
    x = BaseInt(6.50)
    print(str(x))
    y = BaseString("A")
    print(str(x))
    return

def DbgComposite():
    bs = BaseBuySell("BO")
    print(bs.isBuy())
    ma = MyObject2("Object1", "01/15/2023")
    ma.toDF()
    sort_example()
    a =BaseCustomStatus('Open')
    print(str(a))
    sort_example()

    return

def round_up_down_Dbg():
    val = 3.14159
    prec = 2

    f = BaseFloat(val)
    print(f.roundup(prec))
    print(f.rounddown(prec))
    print(f.roundit())

    return

def Dbg_save_file():
    a = BaseObject()
    # Sample data: Replace this with your actual data loading process
    data = {
        'symbol': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL', 'MSFT', 'MSFT', 'TSLA', 'TSLA'],
        'date': ['2023-01-01', '2023-06-01', '2023-01-01', '2022-11-01', '2023-01-01', '2022-10-01', '2023-01-01',
                 '2022-08-01'],
    }

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # listOfInterest = {'Results': [],  'Errors': []}
    listOfInterest = {"DF": df, "DF2" : df }
    a._saveResults(listOfInterest, alt_output_file, altFilename=alt_output_file)
    return

def DbgLogger():

    # Instantiate the Logger class
    logger = Logger("MyApp").get_logger()

    # Log messages
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")
    return

def howToInstallThisLib():
    # pip install -e .
    # pip install -e .[dev]
    # pip install -e .[test]

    # Following two steps - to build and install on lib side
    # pwd
    # G:\My Drive\Software\PycharmProjects\base_lib
    # python setup.py sdist bdist_wheel
    # '''
    # python.exe -m pip install --force-reinstall .\dist\base_lib-0.1.1-py3-none-any.whl
    # '''

    # On App side - restart app to get latest changes
    return


if __name__ == '__main__':
    from common_include import *
    # from common_include import MFList
    # print(MFList)
    # DbgComposite()
    # print({"UnitDbg" : unittest})
    # DbgLogger()  # Comeback for Dbging timeEST
    howToInstallThisLib()
    # Dbg_save_file()
    # DbgBaseDate()
    bf = BasePrice(2.2525)
    df_bf = bf.export_class_data_to_df()
    print(df_bf)
    # bf= bf*1000.0
    print(bf.isPennyStock())
    print(bf)
    round_up_down_Dbg()
    Dbg_save_file()
    a = BaseMoney(1)
    DbgBasics()
    DbgBaseDate()
    DbgBaseFltMnyPerc()