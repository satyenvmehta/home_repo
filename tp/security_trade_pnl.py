from __future__ import annotations

from tp.all_history import Historys
import argparse
from pathlib import Path
from typing import Optional

import pandas as pd

today_dt = pd.Timestamp("today").normalize()
today_yymmdd = today_dt.strftime("%Y-%m-%d")

def parse_money(value: object) -> float:
    """Convert '$1,234.56' or '($1,234.56)' into a float."""
    if pd.isna(value):
        return 0.0

    text = str(value).strip().replace("$", "").replace(",", "")
    is_parenthesized_negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")

    number = float(text) if text else 0.0
    return -number if is_parenthesized_negative else number

def calculate_security_pnl(
        hs
) -> pd.DataFrame:

    df = hs.to_df()

    bad_quantity_mask = df["Quantity"].isna()

    if bad_quantity_mask.any():
        bad_rows = df.loc[
            bad_quantity_mask,
            ["Symbol", "Date", "Quantity", "Price", "Amount"],
        ].copy()

        # Add 2 because:
        # pandas index starts at 0, and Excel/CSV row 1 is the header.
        bad_rows["CSVRowNumber"] = bad_rows.index + 2

        raise ValueError(
            "Invalid Quantity values found:\n"
            + bad_rows.to_string(index=False)
        )

    # start = pd.Timestamp(sell_start_date) if sell_start_date else None
    # end = pd.Timestamp(sell_end_date) if sell_end_date else None
    start = None
    end = None

    if start is not None and end is not None and start > end:
        raise ValueError("sell_start_date cannot be after sell_end_date")

    # Buy history: use all buys available through the reporting end date.
    buy_mask = df["Quantity"] > 0
    if end is not None:
        buy_mask &= df["Date"] <= end
    buys = df.loc[buy_mask].copy()

    # Sell activity: optionally restrict only the sells being evaluated.
    sell_mask = df["Quantity"] < 0
    if start is not None:
        sell_mask &= df["Date"] >= start
    if end is not None:
        sell_mask &= df["Date"] <= end
    sells = df.loc[sell_mask].copy()

    buys["BuyQty"] = buys["Quantity"]
    buys["BuyCost"] = buys["Amount"].abs()

    sells["SellQty"] = sells["Quantity"].abs()
    sells["SellProceeds"] = sells["Amount"].abs()

    buy_summary = (
        buys.groupby("Symbol", as_index=True)
        .agg(
            BuyTransactions=("BuyQty", "size"),
            TotalBuyQty=("BuyQty", "sum"),
            TotalBuyCost=("BuyCost", "sum"),
            FirstBuyDate=("Date", "min"),
            LastBuyDate=("Date", "max"),
        )
    )

    sell_summary = (
        sells.groupby("Symbol", as_index=True)
        .agg(
            SellTransactions=("SellQty", "size"),
            TotalSellQty=("SellQty", "sum"),
            TotalSellProceeds=("SellProceeds", "sum"),
            FirstSellDate=("Date", "min"),
            LastSellDate=("Date", "max"),
        )
    )

    result = buy_summary.join(sell_summary, how="outer").fillna(
        {
            "BuyTransactions": 0,
            "TotalBuyQty": 0.0,
            "TotalBuyCost": 0.0,
            "SellTransactions": 0,
            "TotalSellQty": 0.0,
            "TotalSellProceeds": 0.0,
        }
    )

    result["BuyTransactions"] = result["BuyTransactions"].astype(int)
    result["SellTransactions"] = result["SellTransactions"].astype(int)

    result["AvgBuyPrice"] = result["TotalBuyCost"].div(
        result["TotalBuyQty"].replace(0, pd.NA)
    )
    result["AvgSellPrice"] = result["TotalSellProceeds"].div(
        result["TotalSellQty"].replace(0, pd.NA)
    )

    result["MatchedQty"] = result[["TotalBuyQty", "TotalSellQty"]].min(axis=1)
    result["PnLPerShare"] = result["AvgSellPrice"] - result["AvgBuyPrice"]
    result["PnL"] = result["PnLPerShare"] * result["MatchedQty"]
    result["ReturnPct"] = result["PnLPerShare"].div(result["AvgBuyPrice"]) * 100

    result["RemainingBuyQty"] = (
        result["TotalBuyQty"] - result["MatchedQty"]
    ).clip(lower=0)
    result["UnmatchedSellQty"] = (
        result["TotalSellQty"] - result["MatchedQty"]
    ).clip(lower=0)

    result = result.reset_index()

    money_columns = [
        "TotalBuyCost",
        "AvgBuyPrice",
        "TotalSellProceeds",
        "AvgSellPrice",
        "PnLPerShare",
        "PnL",
        "ReturnPct"
    ]
    result[money_columns] = result[money_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    # result[decimal_columns] = result[decimal_columns].round(2)
    result[money_columns] = result[money_columns].round(2)
    # result["AvgSellPrice"] = result["AvgSellPrice"].round(2)

    # result["ReturnPct"] = result["ReturnPct"].round(2)

    column_order = [
        "Symbol",
        "PnL",
        "ReturnPct",
        "MatchedQty",
        "PnLPerShare",

        "TotalBuyCost",
        "TotalSellProceeds",

        "BuyTransactions",
        "TotalBuyQty",
        "AvgBuyPrice",
        "SellTransactions",
        "TotalSellQty",
        "AvgSellPrice",

        "RemainingBuyQty",
        "UnmatchedSellQty",
        "FirstBuyDate",
        "LastBuyDate",
        "FirstSellDate",
        "LastSellDate",
    ]
    result = result[column_order]
    from tp.pnl_summary import add_summary_row
    result = add_summary_row(result)

    return result #

# Symbol	PnL	ReturnPct	MatchedQty	PnLPerShare	TotalBuyCost	TotalSellProceeds

if __name__ == "__main__":
    csv_out = r"c:/tmp/security_pnl_summary" + today_yymmdd + ".csv"
    hs = Historys()
    result = calculate_security_pnl(hs)
    result.to_csv(csv_out, index=False, date_format="%Y-%m-%d")
    print(result.to_string(index=False))
    print(f"\nSaved: {csv_out}")

