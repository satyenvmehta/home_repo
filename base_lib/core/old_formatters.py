
'''


from tp.stock_screener import RSI_OVERBOUGHT, RSI_OVERSOLD
from enum import Enum

class ConditionOp(Enum):
    GT  = ">"     # greater than
    LT  = "<"     # less than
    GTE = ">="    # greater than or equal
    LTE = "<="    # less than or equal
    EQ  = "=="    # equal
    BETWEEN = "between"
    CONTAINS = "contains"
from enum import Enum

class FillColor(Enum):
    YELLOW = "FFFF00"
    GREEN  = "CCFFCC"
    RED    = "FFC7CE"
    BLUE   = "ADD8E6"

ConditionOp = {
    ConditionOp.GT: "greater than",
    ConditionOp.LT: "less than",
    ConditionOp.GTE: "greater than or equal",
    ConditionOp.LTE: "less than or equal",
    ConditionOp.EQ: "equal",
    ConditionOp.BETWEEN: "between"
    , ConditionOp.CONTAINS: "contains"
}

class Condition:
    def __init__(self, op: ConditionOp, value, color):
        self.op = op
        self.value = value
        self.color = color

def xlswriter_formatter(sheet, workbook, df, sheet_name):
    max_cols = df.shape[1]
    max_rows = df.shape[0]
    J_range = f'J2:J{max_rows}'
    sheet.conditional_format(J_range, {'type': 'cell',
                                                'criteria': 'greater than',
                                                'value': RSI_OVERBOUGHT,
                                                'format': workbook.add_format({'bg_color': '#C6EFCE',
                                                                               'font_color': '#006100'})})
    sheet.conditional_format(J_range, {'type': 'cell',
                                                'criteria': 'less than',
                                                'value': RSI_OVERSOLD,
                                                'format': workbook.add_format({'bg_color': '#FFC7CE',
                                                                               'font_color': '#9C0006'})})

'''