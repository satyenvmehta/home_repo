import os.path
from dataclasses import dataclass, field
from typing import List, Any

from pprint import pprint
from pprint import pprint as print

from pandas import DataFrame

# from all_history import History
# from common_include import load_data_to_class_list, get_load_fun_basedon_cls
# from file_process import FileObject
import pandas as pd
from base_lib.core.base_classes import *
# from tp.lib.tp_classes import BaseTradePrice


# from sympy import Symbol


@dataclass
class BaseContainer(BaseObject):
    def __post_init__(self):
        self.setBase([])
        # self.item = list()
        return

    def append(self, obj):
        self.getBase().append(obj)
        pass

    def remove(self, item):
        my_list = self.getBase()
        value_to_remove = item
        for i in range(len(my_list) - 1, -1, -1):
            if my_list[i] == value_to_remove:
                del my_list[i]
        # self.print()
        return

    def print(self, id=None):
        if not id:
            pprint(self.getBase())
        else:
            if isinstance(self.getBase()[id], BaseObject):
                self.getBase()[id].print()
            else:
                print(self.getBase()[id])
        return

    def _exists(self, obj):
        if obj in self.getBase():
            return True
        return False

    def size(self):
        return len(self.getBase())

    def notEmpty(self):
        return self.size() > 0

    def isEmpty(self):
        return self.size() == 0

    def sort(self, data=None, key=None, reverse=False):
        if not data:
            if isinstance(self, BaseContainer):
                data = self.getBase()  # In case sended is BaseContainer
                if not data:
                    return None
        sdata = sorted(data, key=key, reverse=reverse)
        return sdata

    def getFirst(self):
        item = self.getBase()[0]
        return item

    def saveToCSV(self, fileName=None, header=None):
        if not fileName:
            fileName = "data.csv"
        if os.path.exists(fileName):
            os.remove(fileName)
            print("File " + fileName + " deleted")


        # return
        df = self.export_class_data_to_df()
        if header:
            if isinstance(header, list):
                df.columns = header
        df.to_csv(fileName, index=False)
        print("Data saved to " + fileName)

        return

    def export_class_data_to_df(self):
        df = DataFrame()
        for item in self.getBase():
            if isinstance(item, BaseObject):
                df = pd.concat([df, item.export_class_data_to_df()], ignore_index=True)
            else:
                df = pd.concat([df, pd.DataFrame([item])])

                # df = pd.concat([df, item.export_class_data_to_df()], ignore_index=True)
        return df


@dataclass
class BaseList(BaseContainer):
    def __post_init__(self):
        self.setBase([])
        return

    def append(self, obj):
        if not isinstance(obj, BaseObject):
            obj = BaseString(obj)
        self.getBase().append(obj)
        return

    def print(self):
        print(self.getBase())
        return

@dataclass
class BaseDict(BaseContainer):
    def __post_init__(self):
        self.setBase(dict())
        return

    def setKeyValue(self, k, v):
        base = self.getBase()
        if isinstance(base, dict):
            base[k] = v
        return

    def append(self, key, value):
        if key is BaseObject:
            key = key.getBase()
        self.setKeyValue(key, value)
        # print(key + " " + value)
        return

    def items(self):
        return self.getBase().items()

    def print(self):
        for key, val in self.getBase().items():
            print("Key " + str(key) + " value " + str(val))
        return

    def getKeys(self):
        base = self.getBase()
        if isinstance(base, dict):
            keys = base.keys()
        return keys

    def getKeyList(self):
        return list(self.getKeys())

    def convertContainerToThis(self, container):
        if isinstance(container, dict):
            for k, v in container.items():
                self.setKeyValue(k, v)
            return self
        if isinstance(container, list):
            for item in container:
                self.setKeyValue(item, None)
        return self

    def getValue(self, key):
        try:
            val = self.getBase()[key]
            return val
        except KeyError:
            print("Key " + key + " not found")
            return None


@dataclass
class BaseSet(BaseContainer):
    def __post_init__(self):
        self.setBase(set())
        self.counter = BaseDict()
        return

    def getCounts(self, obj):
        return self.counter.getValue(obj)

    def append(self, obj):
        if not isinstance(obj, str):
            obj = str(obj)
        if super()._exists(obj):
            self.counter.append(obj, self.counter.getValue(obj)+1)
            # self.counter[obj] = self.counter[obj] + 1
            return False  # did not append
        self.getBase().add(obj)
        self.counter.append(obj, 0)    # self.counter[obj] = 0  Initially
        return True  # did append

    def has(self, listVal):
        for item in listVal:
            if item not in self.getBase():
                return False
        return True

    def hasOnly(self, val):
        return (len(self.getBase()) == 1) and val in self.getBase()

    def print(self, id=None):
        if not id:
            pprint(self.getBase())
            print("Details:")
            self.counter.print()
        else:
            if isinstance(self.getBase()[id], BaseObject):
                self.getBase()[id].print()
            else:
                print(self.getBase()[id])
        return

@dataclass
class BaseTuple(BaseContainer):
    def __post_init__(self):
        self.setBase(tuple())
        return

    def append(self, obj):
        self.getBase().append(obj)
        return

@dataclass
class BuySellSet(BaseSet):
    def _multiEntries(self, obj):
        if not self.has(obj):
            return False
        return super().getCounts(obj) > 0

    def multiBuyCounts(self):
        return self._multiEntries('B')

    def multiSellCounts(self):
        return self._multiEntries('S')

    def isBuyOnly(self):
        return self.hasOnly('B')

    def isSellOnly(self):
        return self.hasOnly('S')

    def isBuyAndSellSet(self):
        return self.has(['B', 'S'])

@dataclass
class BaseDF(BaseContainer):
    def __post_init__(self):
        self.setBase(DataFrame())
        return

    def read(self):
        pass

    def getDetailsBySymbol(self, symbol, cls):
        for item in self.getBase():
            if isinstance(item, cls):
                if item.Symbol == symbol:
                    return item
            else:
                print("Invalid class item in list: " + str(type(item)))
        return None

    def getDetailListBySymbol(self, symbol, cls):
        results = BaseList()
        for item in self.getBase():
            if isinstance(item, cls):
                if item.Symbol == symbol:
                    results.append(item)
            else:
                print("Invalid class item in list: " + str(type(item)))
        return results

# from common_include import create_rows_to_class_list
@dataclass
class BaseFileObject(BaseObject):
    def __post_init__(self):
        return

    def deleteLastLine(self):
        with open(self.item, "r+") as f:
            current_position = previous_position = f.tell()
            while f.readline():
                previous_position = current_position
                current_position = f.tell()
            f.truncate(previous_position)
        return

    def getOutFileName(self):
        outdir = os.path.dirname(self.getBase()) + "\\Backup\\"
        fname = os.path.basename(self.getBase()) + "." + getTodayYYYYMMDD() + ".csv"
        outfile = outdir + fname
        return outfile

    def read(self, index_col=None, skip=0, cls=None, skipfooter=1, extra_cols=None):
        # if remove_trailer:
        #     self.deleteLastLine()
        infile = self.getBase()
        outfile = self.getOutFileName()
        with (open(outfile, 'w') as fout, open(infile) as fin):
            fout.write(fin.read())
        # self.df  = pd.read_csv(self.getBase(), index_col=index_col, skiprows=skip, skipfooter=skipfooter, engine='python')
        self.df = pd.read_csv(self.getBase(),  skiprows=skip, skipfooter=skipfooter, engine='python')
        self.df_list = None
        if cls:
            self.remove_extra_columns(self.df, extra_cols=extra_cols)
            self.df_list = self.create_rows_to_class_list(cls, self.df.values.tolist())
        else:
            self.df_list = self.df
        if index_col:
            self.df.set_index(keys=index_col)
        return self.df_list

    # def load_data_to_class_list(self, cls)->list:
    #     lamfun = get_load_fun_basedon_cls(cls)
    #     if lamfun:
    #         return list(map(lamfun, self.df.values.tolist()))
    #     return None

    def crete_row_values_to_class(self, cls, row):
        annos = cls.__annotations__
        data_dict = {}
        colid = 0
        for name, typ in annos.items():
            # import trade_import
            # from tp.market.TradeUtil import BaseTradeSymbol, BaseTrade, BaseTrades,  BaseTradePrice
            data_dict[name] = typ(row[colid])
            colid = colid + 1
        cls_inst = cls.from_dict(data_dict)
        # cls_inst._postRowRead()
        return cls_inst

    def create_rows_to_class_list(self, cls, rows):
        class_list = []
        for row in rows:
            cls_inst = self.crete_row_values_to_class(cls, row)
            class_list.append(cls_inst)
        return class_list

    def create_classval_to_row(self, cls, row):
        pass

@dataclass
class BaseReaderWriter(BaseDF):
    def init_nones(self):
        self.fo = None
        self.df_list = None
        self.extra_columns = None
        self.index_cols = None
        self.export_df = pd.DataFrame()
        return
    def __post_init__(self):
        super(BaseReaderWriter, self).__post_init__()
        self.cls = None
        self.uniqueCols = None
        self.uniqueRows = None

        self.fo = None
        self.df_list = None
        self.extra_columns = None
        self.export_df = pd.DataFrame()
        # self.updateDFDescriptionToBS()
        return
    def setDataFrame(self, df):
        self.df_list = df
        return

    def getDF(self):
        if self.df_list:
            return self.df_list
        if self.fo:
            return self.fo.df
        return None

    # def setIndexCols(self, idx_cols):
    #     if isinstance(self.fo, BaseFileObject):
    #         self.fo.setIndexCols(idx_cols=idx_cols)
    #     return
    def read(self, header_lines, file2read, skipfooter=1):
        print("Reading " + self.cls.__name__ + " from " + file2read)
        self.df_list = None
        self.header_lines = header_lines
        self.skipfooter = skipfooter
        self.fo = BaseFileObject()
        self.fo.setBase(file2read)
        results = self.fo.read(skip=self.header_lines, cls=self.cls, skipfooter=skipfooter, index_col=self.index_cols, extra_cols=self.extra_columns)
        self.setBase(results)   # Override with original DataFrame from BaseDF with DF read just now
        # self._postReadProcess()
        return self.getBase()

    def _postReadProcess(self):
        for item in self.getBase():
            item._postRowRead()
        return self.getBase()

    def print(self):
        print(self.getBase())
        return

    def examinRow(self, row2Examin):
        if not self.getBase():
            print("examinRow: self.item is None")
            return
        offset = self.header_lines + 1 + 1
        actual_row = row2Examin - offset

        self.getBase()[actual_row].print()
        return actual_row

    def getUniqueRows(self, colList=None):
        if not colList:
            if not self.uniqueCols:
                print("Please set uniqueCols")
                return None
            colList = self.uniqueCols
        self.uniqueRows  = self.getDF().drop_duplicates(subset=self.uniqueCols)
        return self.uniqueRows

    def getUniqueValuesForCol(self, colName):
        df = self.getDF()
        uvals = df[colName].unique()
        return sorted(uvals)


    def getDetailsBySymbol(self, symbol):
        for item in self.getBase():
            if isinstance(item, self.cls):
                if item.Symbol == symbol:
                    return item
        return None

    def process(self, method):
        for row in self.getBase():
            rc = method(row)
        return rc

    def setClassMembersByTypes(self, cls):
        self.colFormats = BaseDict()
        for member, mtype in self.getClassMembers(cls).items():
            frmt = None
            if mtype in [BaseMoney, BasePercentage, BaseInt, BaseFloat]:
                frmt = mtype.format_str
                self.colFormats.append(member, frmt)
        return

    def getClassMembersFormats(self):
        if not self.colFormats:
            self.setClassMembersByTypes(self.cls)
        return self.colFormats.getBase()

    def export_class_data_to_df(self):
        # Create an empty DataFrame
        # self.export_df = pd.DataFrame()
        if len(self.export_df) > 1:
            return self.export_df
        class_instances = self.getBase()
        for instance in class_instances:
            data = {}
            for key, value in instance.__dict__.items():
                if value:
                    if isinstance(value, BaseObject):
                        val = value.getBase()
                    else:
                        val = value
                    data[key] = [val]
                    # dtypes[key] = 'object'  #type(val)
                else:
                    data[key] = None
                    # dtypes[key] = 'object'
            instance_df = pd.DataFrame(data) #, dtype=dtypes)
            # frmts = self.get
            self.export_df = pd.concat([self.export_df, instance_df], ignore_index=True)
            self.assignFormats()
        return self.export_df

    def assignFormats(self):
        formats = self.getClassMembersFormats()
        for membr, frmt in formats.items():
            self.export_df[membr] = pd.to_numeric(self.export_df[membr], errors='coerce')
        return self.export_df

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

def DbgBaseList():
    bsl = BaseList()
    # bsl.append("item1")
    # bsl.append("item2")
    # bsl.saveToCSV()
    for i in objects:
        bsl.append(i)

    bsl.saveToCSV("TestObj.csv")
    bsl.print()
    name2 = BaseString("Object2")
    bsl.remove(item=name2)
    bsl.print()
    return

def DbgBSType():
    bs = BuySellSet()
    lsd = bs.toListOfDict()
    m = bs.getLocalMembers()
    bs.append('B')
    bs.append('S')

    print(bs.multiBuyCounts())
    print(bs.isBuyOnly())

    bs.append('S')
    print(bs.isBuyOnly())
    print(bs.isBuyAndSellSet())
    return

def Dbg_find_docs():
    documents = [
        {"a1": "val1", "a2": "val2", "a3": "val3", "a4": "val4", "a5": "val5"},
        {"a1": "val1", "a2": "val2", "a3": "val31", "a4": "val41", "a5": "val5"},
        {"a11": "val11", "a2": "val2", "a3": "val31", "a4": "val41", "a5": "val51"},
    ]

    filter_values = {"a1": "val1", "a2": "val2", "a5": "val5"}

    # Find documents that match all key-value pairs in filter_values
    matching_documents = [
        doc for doc in documents if all(doc.get(k) == v for k, v in filter_values.items())
    ]

    # Print results
    print(matching_documents)

def DbgBaseSet():
    bs = BaseSet()
    # cmo = cmpdObj("BABA", "BUY")
    # rc = bs.append(cmo)
    # rc = bs.append(cmo)
    bs.append(1)
    bs.append(2)
    bs.append(1)
    bs.saveToCSV(header=["Numbers"])

    bs.print()
    return

# from common_include import *
if __name__ == '__main__':
    DbgBaseSet()
    Dbg_find_docs()
    DbgBSType()
    DbgBaseList()
    bf = BaseDF()
    b = bf.getBase()
    print(b)
    brw = BaseReaderWriter()
    print(brw.getBase())

    bd = BaseDict()
    bd.append("k11", "Value1")
    bd.append("k12", "Value12")
    bd.append("k13", "Value13")
    bd.print()

    x = BaseFloat(10.234)
    print(str(x))
    x = BaseMoney(100.226)
    print(str(x))
    x = BasePercentage(10.234)
    print(str(x))


    bs = BaseBuySell("BO")
    print(bs.isBuy())

    z = BaseDate("11/23/2023")
    print(z.getNoDaysFromToday())

    z = BaseDate(None)
    print(z.getNoDaysFromToday())

    ma = MyObject2("Object1", "01/15/2023")
    x = ma.toDF()
    sort_example()
    # tp = TradeProcessing()
    # row2Examin = 16
    # tp.examinRow(row2Examin)

    # tp.saveResults()


    a =BaseCustomStatus('Open')
    print(str(a))
    sort_example()
    a = "03/20/2020"
    b = "01/20/2021"
    b = "12/01/2020"
    print(BaseDate(a))
    print(str(BaseDate(a)))
    print(getTodayYYYYMMDD())
    x = BaseFloat(10.234)
    print(str(x))
    x = BasePercentage(10.234)
    print(str(x))
    x = BaseMoney(10.245)
    print(str(x))
    x = int(5.4)
    print(x)
    x = BaseInt(6.50)
    print(str(x))
    x = BaseString("A")
    print(str(x))
    x = BaseMoney(100.226)
    print(str(x))

