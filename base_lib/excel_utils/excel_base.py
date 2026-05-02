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

if __name__ == "__main__":
    ExcelFileBase(filen, df_dict, apply_formatter)
