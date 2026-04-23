from __future__ import annotations

import common_include as C
from base_lib.etl.base_load import DataFrameLoad, CSVLoad


@C.dataclass
class Trade(C.BaseObject):
    TradeId: int
    CustomerId: int
    Amount: float

    @classmethod
    def from_dict(cls, d: dict) -> "Trade":
        return cls(
            TradeId=int(d["TradeId"]) if d.get("TradeId") is not None else None,
            CustomerId=int(d["CustomerId"]) if d.get("CustomerId") is not None else None,
            Amount=float(d["Amount"]) if d.get("Amount") is not None else None,
        )


from base_lib.core.base_classes import BaseRowModel
@C.dataclass
class Trade1(C.BaseRowModel):
    TradeId: int = None
    CustomerId: int = None
    Amount: float = None

import pandas as pd

trades_df = pd.DataFrame({
    "TradeId": [1, 2, 3],
    "CustomerId": [101, 102, 103],
    "Amount": [1000.0, 2500.0, None],
})

load = C.DataFrameLoad(
    Name="Trades12",
    LoadType="main",
    SourceDf=trades_df,
    RequiredColumns=["TradeId", "CustomerId", "Amount"],
    TargetClass=Trade1,
)

load_csv = C.CSVLoad(
    Name="Trades",
    FilePath="trades.csv",
    LoadType="main",
    TargetClass=Trade,
)

def run_load(load):
    result = load.run()

    print("IsValid:", result.IsValid)
    print("RowCount:", result.RowCount)
    print("PreparedData:")
    print(result.PreparedData)

    print("\nObjectList:")
    for obj in result.ObjectList or []:
        print(obj)

    print("\nErrors:")
    for err in result.Errors:
        print(err)

run_load(load=load)
run_load(load=load_csv)