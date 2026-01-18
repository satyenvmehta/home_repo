
import common_include as C
from base_lib.core.files_include import int_scan_file
from tp.TradeUtil import BaseTrade, BaseTrades, Symbol

header_lines = 0

PossibleTrends = {'UP', 'DOWN', 'BOTH', 'NONE'}

class Trend(C.BaseObjectItem):
    def __post_init__(self):
        if not self.getBase().upper() in PossibleTrends:
            raise "Error"
        return
    def getValue(self):
        if self.getBase().upper().__eq__("UP"):
            return 1
        if self.getBase().upper().__eq__("DOWN"):
            return -1
        return 0

@C.dataclass
class InteliScan(BaseTrade):
    Market:C.BaseString = None
    Symbol:C.BaseString = None
    Category:C.BaseString = None
    TrplXDir: Trend = None
    TrplXDays:C.BaseString = None
    TrplXVal:C.BaseString = None
    NutrlTrndDir: Trend = None
    NutrlTrndDays:C.BaseString = None
    ShrtTermDiffDir: Trend = None
    ShrtTermDays:C.BaseString = None
    MidTermDir: Trend = None
    MidTermDays:C.BaseString = None
    LongTermDir: Trend = None
    LongTermDays:C.BaseString = None
    PredTradDir: Trend = None
    Volume:C.BaseString = None
    VolumePecAvg:C.BaseString = None
    ShortTermTrendDir: Trend = None
    sttdays:C.BaseString = None
    MediumTermTrendDir: Trend = None
    mttdays:C.BaseString = None
    LongTermTrendDir: Trend = None
    lttdays:C.BaseString = None

    @classmethod
    def from_dict(cls, data_dict):
        cls_inst =  cls(data_dict['Market'],	data_dict['Symbol'],	data_dict['Category'],\
        data_dict['TrplXDir'],	data_dict['TrplXDays'],	data_dict['TrplXVal'],	\
        data_dict['NutrlTrndDir'],	data_dict['NutrlTrndDays'],	data_dict['ShrtTermDiffDir'],\
        data_dict['ShrtTermDays'],	data_dict['MidTermDir'],	data_dict['MidTermDays'],\
        data_dict['LongTermDir'],	data_dict['LongTermDays'],	data_dict['PredTradDir'],\
        data_dict['Volume'],	data_dict['VolumePecAvg']
        , data_dict['ShortTermTrendDir'], data_dict['sttdays']
        ,	data_dict['MediumTermTrendDir'],	data_dict['mttdays']
        ,	data_dict['LongTermTrendDir'],	data_dict['lttdays'])

        cls_inst.calcScore()
        return cls_inst

    def getTSML(self):
        res = self.TrplXDir.getBase()+"|"+self.ShrtTermDiffDir.getBase()+"|"+self.MidTermDir.getBase()+"|"+self.LongTermDir.getBase()
        return res

    def _getScoreNum(self, direct):
        if isinstance(direct, Trend):
            return direct.getValue()
        raise "Error _getScoreNum"

    def calcScore(self):
        self.score = self.TrplXDir.getValue() + self.LongTermDir.getValue() + self.MidTermDir.getValue() + self.ShrtTermDiffDir.getValue() + \
                     self.NutrlTrndDir.getValue() + self.PredTradDir.getValue() + \
                     self.ShortTermTrendDir.getValue() + self.MediumTermTrendDir.getValue() + self.LongTermTrendDir.getValue()
        return

@C.dataclass
class InteliScans(BaseTrades):
    def __post_init__(self):
        super().__post_init__()
        self.cls = InteliScan
        self.uniqueCols = ['Symbol',	'Last',	'% Chg',	'Day Range',	'Sector',	'52 Wk Range',	'Volume',]
        self.readFile(self.cls, self.uniqueCols, header_lines=header_lines, datafile=int_scan_file)
        df = self.getDF()
        self.all_symbols = df[Symbol].unique()
        return

if __name__ == '__main__':
    b = InteliScans()
    print(b.getUniqueSymbols())
    # b.print()
    row2Examin = 16
    b.examinRow(row2Examin)
    obj = b.findSymbol('AAPL')
    if isinstance(obj, InteliScan):
        print(obj.getTSML() + " " + str(obj.score))

    # offset = header_lines+1+1
    # actual_row = row2Examin-offset
    # print(int_scan_list[actual_row])
    # print(b.getDetailsBySymbol('AAPL', InteliScan))