from pathlib import Path
import pandas as pd


from tp.excel_classes import create_excel_file, FillColor, ConditionOp, Condition

df_summary = pd.DataFrame({
    "Metric": ["Revenue", "Cost", "Profit"],
    "Value": [1200, 800, 400]
})

def formatter(excel):
    excel.fill_range("Summary", "A1:B1", FillColor.YELLOW)
    excel.conditional_format(
        "Summary",
        "B2:B10",
        Condition(ConditionOp.GT, 1000, FillColor.RED)
    )

full_path = Path("C:/tmp/report1.xlsx")
if __name__ == "__main__":
    excel = create_excel_file(full_path, "create")
    excel.apply_formatter(formatter)
    excel.save()

# file written here
