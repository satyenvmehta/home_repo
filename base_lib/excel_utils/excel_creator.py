# ============================================================
# excel_creator.py
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import sleep
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from base_lib.core.base_container_classes import BaseReaderWriter
from base_lib.excel_utils.excel_base import ExcelFileBase, Condition, ConditionOp, FillColor



@dataclass
class ExcelCreator(ExcelFileBase):
    """
    Create-time Excel writer backed by pandas + xlsxwriter.

    Usage:
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            excel = ExcelCreator(path=Path(path), writer=writer)
            excel.add_sheet("Summary", df_summary)
            excel.fill_row_for_df("Summary", 1, df_summary, FillColor.YELLOW)
            excel.border_all_sheets()
            # file finalized when 'with' block exits OR when excel.save() is called
    """
    writer: pd.ExcelWriter | None = None

    # cache formats to avoid format explosion
    _formats: Dict[str, Any] = field(default_factory=dict)

    # sheet -> (nrows, ncols) used for data-aware borders/ranges
    _sheet_dims: Dict[str, Tuple[int, int]] = field(default_factory=dict)

    def __post_init__(self):
        if self.writer is None:
            # You may still use it without a with-block if you want,
            # but most users will pass writer from `with pd.ExcelWriter(...) as writer`.
            self.writer = pd.ExcelWriter(self.path, engine="xlsxwriter")

        self.workbook = self.writer.book
        self.sheets = {}  # will be filled in add_sheet()

    # ----------------------------
    # Sheet creation
    # ----------------------------
    def add_sheet(self, name: str, df: pd.DataFrame, index: bool = False) -> None:
        df.to_excel(self.writer, sheet_name=name, index=index)
        self.sheets[name] = self.writer.sheets[name]

        # store "used range" dimensions (include header row)
        nrows = df.shape[0] + 1
        ncols = df.shape[1]
        self._sheet_dims[name] = (nrows, ncols)
        self.common_formatting_for_sheet(name, df)
        return

    # ----------------------------
    # Format helpers
    # ----------------------------
    def _fmt_fill(self, color: FillColor):
        key = f"fill:{color.value}"
        if key not in self._formats:
            self._formats[key] = self.workbook.add_format({"bg_color": f"#{color.value}"})
        return self._formats[key]

    def _fmt_border_thin(self):
        key = "border:thin"
        if key not in self._formats:
            self._formats[key] = self.workbook.add_format({"border": 1})
        return self._formats[key]

    # ----------------------------
    # Base API implementations
    # ----------------------------
    def fill_cell(self, sheet: str, cell: str, color: FillColor) -> None:
        ws = self.get_sheet(sheet)
        r, c = self.cell_to_rc(cell)
        ws.write(r, c, "", self._fmt_fill(color))
        return

    def fill_range(self, sheet: str, cell_range: str, color: FillColor) -> None:
        ws = self.get_sheet(sheet)
        # xlsxwriter trick: apply a static format to every cell in the range
        ws.conditional_format(cell_range, {"type": "no_errors", "format": self._fmt_fill(color)})
        return

    def fill_row(self, sheet: str, row: int, color: FillColor) -> None:
        # STRUCTURAL: applies to entire row (Excel semantics)
        ws = self.get_sheet(sheet)
        ws.set_row(row - 1, None, self._fmt_fill(color))
        return

    def fill_column(self, sheet: str, col: int, color: FillColor) -> None:
        ws = self.get_sheet(sheet)
        ws.set_column(col - 1, col - 1, None, self._fmt_fill(color))
        return

    def fill_row_for_df(self, sheet: str, row: int, df: pd.DataFrame, color: FillColor) -> None:
        """
        Data-aware header fill: colors only the DataFrame's actual columns.
        """
        last_col = df.shape[1]
        rng = f"A{row}:{self.col_letter(last_col)}{row}"
        self.fill_range(sheet, rng, color)
        return

    def conditional_format(self, sheet: str, cell_range: str, condition: Condition) -> None:
        ws = self.get_sheet(sheet)
        fmt = self._fmt_fill(condition.color)
        if condition.op == ConditionOp.BETWEEN:
            low, high = condition.value
            ws.conditional_format(cell_range, {
                "type": "cell",
                "criteria": "between",
                "minimum": low,
                "maximum": high,
                "format": fmt
            })
        elif condition.op == ConditionOp.CONTAINS:
            ws.conditional_format(cell_range, {
                "type": "text",
                "criteria": "containing",
                "value": condition.value,
                "format": fmt
            })
        else:
            ws.conditional_format(cell_range, {
                "type": "cell",
                "criteria": condition.op.value,
                "value": condition.value,
                "format": fmt
            })
        return

    def condition_format_row(self, sheet, df, row_id, condition):
        max_col = df.shape[1]
        print("max_col: ", max_col)
        cell_range = rf"A{row_id}:{max_col}{row_id}"
        self.conditional_format(sheet, cell_range, condition)
        return
    def condition_format_col(self, sheet, df, col_name, condition):
        col_id = df.columns.get_loc(col_name) + 1
        cell_range = rf"{col_id}:{col_id}"
        self.conditional_format(sheet, cell_range, condition)
        return

    def border_used_range(self, sheet: str) -> None:
        """
        Borders only where data exists:
        A1:{last_col}{nrows} based on the DataFrame used to create the sheet.
        """
        if sheet not in self._sheet_dims:
            # sheet exists but no recorded df dims (unusual)
            return

        ws = self.get_sheet(sheet)
        nrows, ncols = self._sheet_dims[sheet]
        if nrows <= 0 or ncols <= 0:
            return

        last_col = self.col_letter(ncols)
        rng = f"A1:{last_col}{nrows}"
        ws.conditional_format(rng, {"type": "no_errors", "format": self._fmt_border_thin()})
        return

    def save(self) -> None:
        # If you used a `with pd.ExcelWriter(...) as writer`, the writer closes automatically.
        # Calling save() is fine too.
        self.writer.close()
        return

    # 1) Get stored used dims
    def get_used_dims(self, sheet: str) -> tuple[int, int]:
        """
        Returns (nrows, ncols) for sheet as recorded from the DataFrame used in add_sheet().
        nrows includes header row.
        """
        return self._sheet_dims.get(sheet, (0, 0))

    # 2) Freeze header row + first column (or custom)
    def freeze_panes(self, sheet: str, row: int = 1, col: int = 1) -> None:
        """
        Freeze panes at (row, col) in Excel terms:
          row=1,col=1 freezes top row and first column (like Excel "Freeze Panes")
        Implementation: xlsxwriter uses zero-based indices.
        """
        ws = self.get_sheet(sheet)
        ws.freeze_panes(row, col)
        return

    # 3) Fill first column only where data exists (data-aware)
    def fill_first_col_for_df(self, sheet: str, df: pd.DataFrame, color: FillColor) -> None:
        """
        Fill column A from row 1..nrows (including header), but only for data width.
        """
        nrows = df.shape[0] + 1
        self.fill_range(sheet, f"A1:A{nrows}", color)
        return

    def set_auto_filter_for_df(self, sheet: str, df):
        """
        Apply Excel auto-filter to the used DataFrame range.
        """
        ws = self.get_sheet(sheet)

        nrows = df.shape[0] + 1  # include header
        ncols = df.shape[1]

        if nrows <= 1 or ncols <= 0:
            return

        last_col = self.col_letter(ncols)
        rng = f"A1:{last_col}{nrows}"

        ws.autofilter(rng)

    def auto_col_width_for_df(self, sheet: str, df, *, min_width: int = 5, max_width: int = 15):
        """
        Auto-size columns based on header + stringified cell lengths (approx).
        xlsxwriter uses character width units, so this works well.
        """
        ws = self.get_sheet(sheet)

        for i, col_name in enumerate(df.columns):
            # header length
            best = len(str(col_name))

            # sample the column as strings (fast enough for typical report sizes)
            # if your DF is huge, consider sampling: df[col_name].head(200)
            col_series = df[col_name].astype(str).fillna("")
            max_len = col_series.map(len).max() if len(col_series) else 0

            best = max(best, int(max_len))
            width = min(max(best, min_width), max_width)
            ws.set_column(i, i, width+2)
        return

    def common_formatting_for_sheet(self, sheet_name,  df):
        self.fill_row_for_df(sheet_name, 1, df, FillColor.YELLOW)
        self.fill_first_col_for_df(sheet_name, df, FillColor.BLUE)
        self.freeze_panes(sheet_name, row=1, col=1)
        self.auto_col_width_for_df(sheet_name, df)
        self.set_auto_filter_for_df(sheet_name, df)
        # self.apply_formatter(sheet_name, df)
        return
import os
def validate_writeable_output_files(path):
    while True:
        try:
            os.rename(path, path)
            break
        except PermissionError:
            print("Please close already open file ..", path)
            sleep(3)
    return True

from typing import Callable, Dict, Optional
# Type for app custom formatter:
# def custom_formatter(excel: ExcelCreator, df_dict: dict[str, pd.DataFrame]) -> None
# CustomFormatter = Callable[["ExcelCreator", Dict[str, pd.DataFrame]], None]
CustomFormatter = Callable[[ExcelCreator, pd.DataFrame, str], None]
# ------------------------------------------------------------
# Wrapper function: create_excel(...)
# Put this at module level in excel_creator.py
# ------------------------------------------------------------

def create_excel(
    file_name: str | Path,
    df_dict: Dict[str, pd.DataFrame],
    custom_formatter_method: Optional[CustomFormatter] = None,
    # *
    # header_color: FillColor = FillColor.YELLOW,
    # first_col_color: Optional[FillColor] = FillColor.BLUE,
    # add_borders: bool = True,
    # freeze_header_and_first_col: bool = True,
) -> Path:
    """
    Create an Excel file from a dict of {sheet_name: DataFrame} with common formatting:
      - header row color (data-aware)
      - first column color (data-aware, optional)
      - borders on used range for all sheets (optional)
      - freeze header + first column (optional)
    Then calls custom_formatter_method(excel, df_dict, sheet_name) if provided.

    Returns Path(file_name).
    """
    path = Path(file_name)

    # Use pandas writer lifecycle (file is created when the with-block ends)
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        excel = ExcelCreator(path=path, writer=writer)

        # 1) Create sheets
        print("creating file: ", path)
        for sheet_name, dobj in df_dict.items():
            if isinstance(dobj, BaseReaderWriter):
                df = dobj.export_class_data_to_df()
            else:
                df = dobj
            print("     sheet: ", sheet_name)
            if len(df) > 0:
                excel.add_sheet(sheet_name, df)
            # 2) App-specific formatting
            if custom_formatter_method is not None:
                custom_formatter_method(excel, df, sheet_name)

        # Borders for all sheets (used range = df dims)
        excel.border_all_sheets()

    print("Done")
    return path

if __name__ == "__main__":
    # Example usage
    import pandas as pd
    import common_include as C

    df_summary = pd.DataFrame({"Metric": ["Revenue", "Cost"], "Value": [1200, 800]})
    df_details = pd.DataFrame({"Item": ["A", "B"], "Amount": [50, 200]})
    df_bs = pd.DataFrame({"Ticker": ["AAPL", "MSFT", "ABC"], "Action": ["Buy", "Sell", "Buy_Ign"]})
    df_RYG = pd.DataFrame({"Stock": ["AAPL", "MSFT", "ABC"], "noOfFlips": [1, 3, 5]})
    df_dict = {
        "Summary": df_summary,
        "Details": df_details,
        "BS": df_bs
        ,"RYG":df_RYG
    }

    def my_custom_formatter(excel, df, sheet_name):
        excel.bs_formatter(df, sheet_name, 'B')
        ryg = {'col_name': 'noOfFlips', 'green': 5, 'red': 2}
        excel.custom_RYG_formatter(df, sheet_name, ryg)
        return

    x = C.create_excel(
        r"C:\tmp\report41.xlsx",
        df_dict,
        custom_formatter_method=my_custom_formatter,
    )
    print(x)