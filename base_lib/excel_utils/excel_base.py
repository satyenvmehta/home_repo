# ============================================================
# excel_base.py
# ============================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import re

# from base_lib.core.formatters import FillColor
# import common_include as C

# ----------------------------
# Enums (no magic strings)
# ----------------------------

class FillColor(Enum):
    LIGHT_GRAY = "ADD8E6"
    YELLOW = "FFFF00"
    GREEN  = "CCFFCC"
    RED    = "FFC7CE"
    BLUE   = "ADD8E6"


class ConditionOp(Enum):
    # CONTAINS = None
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    BETWEEN = "between"
    NOT_CONTAINS = "not_contains"
    CONTAINS = "contains"
    def __str__(self):
        return self.value
    def __repr__(self):
        return self.value


@dataclass(frozen=True)
class Condition:
    op: ConditionOp
    value: Any
    color: FillColor


# ----------------------------
# Base abstraction
# ----------------------------

@dataclass
class ExcelFileBase(ABC):
    """
    Base class for Excel operations.

    - `workbook`: engine-specific workbook handle
      - xlsxwriter: xlsxwriter.Workbook via pandas writer.book
      - openpyxl: openpyxl.Workbook
    - `sheets`: maps sheet name -> engine-specific worksheet handle
      - xlsxwriter: xlsxwriter.Worksheet
      - openpyxl: openpyxl.worksheet.worksheet.Worksheet
    """
    path: Path

    workbook: Optional[Any] = None
    sheets: Dict[str, Any] = field(default_factory=dict)

    # ---------- shared helpers ----------
    @staticmethod
    def cell_to_rc(cell: str) -> Tuple[int, int]:
        """
        Convert Excel cell reference (e.g., 'B2') to zero-based (row, col).
        """
        match = re.match(r"([A-Z]+)(\d+)", cell.upper())
        if not match:
            raise ValueError(f"Invalid cell reference: {cell}")

        col_letters, row = match.groups()
        col = 0
        for c in col_letters:
            col = col * 26 + (ord(c) - ord("A") + 1)

        return int(row) - 1, col - 1

    @staticmethod
    def col_letter(col_1_based: int) -> str:
        """
        Convert 1-based column index to Excel column letter (1->A, 27->AA).
        """
        if col_1_based <= 0:
            raise ValueError("col_1_based must be >= 1")

        result = ""
        col = col_1_based
        while col:
            col, rem = divmod(col - 1, 26)
            result = chr(65 + rem) + result
        return result

    @staticmethod
    def get_col_num_by_header(df, header_name: str) -> int:
        """
        Returns 1-based column number.
        """
        for idx, col in enumerate(df.columns, start=1):
            if str(col).upper() == header_name.upper():
                return idx
        return None

        # raise KeyError(f"Column not found: {header_name}")

    # ---------- common sheet access ----------
    def get_sheet(self, sheet: str) -> Any:
        if sheet not in self.sheets:
            raise KeyError(f"Sheet not found: {sheet}. Available: {list(self.sheets.keys())}")
        return self.sheets[sheet]

    def list_sheets(self) -> list[str]:
        return list(self.sheets.keys())

    # ---------- "common method names" contract ----------
    @abstractmethod
    def fill_cell(self, sheet: str, cell: str, color: FillColor) -> None:
        ...

    @abstractmethod
    def fill_range(self, sheet: str, cell_range: str, color: FillColor) -> None:
        ...

    @abstractmethod
    def fill_row(self, sheet: str, row: int, color: FillColor) -> None:
        """
        NOTE:
        - Creator (xlsxwriter): structural row format affects full row.
        - Updater (openpyxl): will apply to used columns (max_column).
        """
        ...

    @abstractmethod
    def fill_column(self, sheet: str, col: int, color: FillColor) -> None:
        ...

    @abstractmethod
    def conditional_format(self, sheet: str, cell_range: str, condition: Condition) -> None:
        ...

    @abstractmethod
    def border_used_range(self, sheet: str) -> None:
        """
        Apply thin borders to A1:MaxColMaxRow where 'used range' is defined
        by the implementation:
        - Creator: based on DataFrame dimensions stored at add_sheet time.
        - Updater: based on ws.max_row / ws.max_column.
        """
        ...

    def border_all_sheets(self) -> None:
        for name in self.list_sheets():
            self.border_used_range(name)

    @abstractmethod
    def save(self) -> None:
        ...

    def get_col_range(self, df, col_id):
        max_rows = df.shape[0] + 1
        range = f'{col_id}2:{col_id}{max_rows}'
        return range
    def get_row_range(self, df, row_id):
        max_cols = df.shape[1]
        range = f'B{row_id}:{self.col_letter(max_cols)}{row_id}'
        return range

    def get_range_by_header(
            self,
            df,
            header_name: str,
            start_row: int = 2
    ):
        col_num = self.get_col_num_by_header(df, header_name)
        if col_num is None:
            return None
        col_id = self.col_letter(col_num)

        last_row = df.shape[0] + 1

        return f"{col_id}{start_row}:{col_id}{last_row}"

    def tf_formatter(self, df, sheet_name, col_id):
        range = self.get_col_range(df, col_id)
        self.conditional_format(
            sheet_name, range, Condition(
                ConditionOp.CONTAINS,
                "TRUE",
                FillColor.GREEN
            ))
        self.conditional_format(
            sheet_name, range, Condition(
                ConditionOp.CONTAINS,
                "FALSE",
                FillColor.RED
            ))
        return

    def bs_formatter(self, df, sheet_name, col_id: str):
        bs_range = self.get_col_range(df, col_id)
        self.conditional_format(
            sheet_name,
            bs_range,
            Condition(
                ConditionOp.CONTAINS,
                "Ign",
                FillColor.LIGHT_GRAY)
        )
        self.conditional_format(
            sheet_name,
            bs_range,
            Condition(
                ConditionOp.CONTAINS,
                "Buy",
                FillColor.GREEN)
        )
        self.conditional_format(
            sheet_name,
            bs_range,
            Condition(
                ConditionOp.CONTAINS,
                "Sell",
                FillColor.RED)
        )
        self.conditional_format(
            sheet_name,
            bs_range,
            Condition(
                ConditionOp.CONTAINS,
                "Hold",
                FillColor.YELLOW)
        )
        return

    def custom_RYG_formatter(self, df, sheet_name, ryg_cond:dict):
        col_name = ryg_cond['col_name']
        range = self.get_range_by_header(df, col_name)
        if not range:
            return
        green = ryg_cond['green']
        red = ryg_cond['red']
        yellow = (red-0.1, green + 0.1)
        self.conditional_format(
            sheet_name, range, Condition(
                ConditionOp.GTE,
                green,
                FillColor.GREEN
            ))
        self.conditional_format(
            sheet_name, range, Condition(
                ConditionOp.LTE,
                red,
                FillColor.RED
            ))
        self.conditional_format(
            sheet_name, range, Condition(
                ConditionOp.BETWEEN,
                yellow,
                FillColor.YELLOW
            ))
        return

# =========  Examples  ============
def apply_formatter(excel, df, sheet_name):
    excel.tf_formatter(df, sheet_name, 'C')
    ryg = {'col_name':'noOfFlips', 'green': 5, 'red': 2}
    excel.custom_RYG_formatter(df, sheet_name, ryg)
    excel.bs_formatter(df, sheet_name, 'E')
    return
if __name__ == "__main__":
    from pathlib import Path
    filen: Path = Path(r'C:\tmp\test.xlsx')
    df_dict = {}

    print(ExcelFileBase.col_letter(27))
    print(ExcelFileBase.cell_to_rc('Z123'))
    print(ExcelFileBase.cell_to_rc('AA123'))
    # This CANT BE CREATED...
    # ExcelFileBase(filen, df_dict)
