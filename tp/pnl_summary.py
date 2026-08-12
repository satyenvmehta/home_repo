import numpy as np
import pandas as pd

def add_summary_row(result: pd.DataFrame) -> pd.DataFrame:

    result = result.copy()

    numeric_columns = [
        "PnL",
        "ReturnPct",
        "MatchedQty",
        "PnLPerShare",
        "TotalBuyCost",
        "TotalSellProceeds",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

    total_pnl = result["PnL"].sum(skipna=True)
    total_buy_cost = result["TotalBuyCost"].sum(skipna=True)
    total_sell_proceeds = result[
        "TotalSellProceeds"
    ].sum(skipna=True)

    portfolio_return_pct = (
        total_pnl / total_buy_cost * 100
        if total_buy_cost != 0
        else np.nan
    )

    summary_row = {
        "Symbol": "Summary",
        "PnL": round(total_pnl, 2),
        "ReturnPct": round(portfolio_return_pct, 2),
        "MatchedQty": np.nan,
        "PnLPerShare": np.nan,
        "TotalBuyCost": round(total_buy_cost, 2),
        "TotalSellProceeds": round(total_sell_proceeds, 2),
    }

    # Preserve any additional columns in result.
    summary_df = pd.DataFrame(
        [summary_row],
        columns=result.columns,
    )

    final = pd.concat(
        [summary_df, result],
        ignore_index=True,
    )
    return final