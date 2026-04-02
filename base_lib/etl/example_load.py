from __future__ import annotations

import common_include as C
from base_lib.etl.base_load import DataFrameLoad


@C.dataclass
class Trade(C.BaseObject):
    TradeId: int
    CustomerId: int
    Amount: float

    @classmethod
    def from_dict(cls, d: dict) -> "Trade":
        return cls(
            TradeId=int(d["trade_id"]),
            CustomerId=int(d["customer_id"]),
            Amount=float(d["amount"]),
        )

import pandas as pd

trades_df = pd.DataFrame({
    "trade_id": [1, 2, 3],
    "customer_id": [101, 102, 103],
    "amount": [1000.0, 2500.0, 9000.0],
})

load = DataFrameLoad(
    Name="Trades",
    LoadType="main",
    SourceDf=trades_df,
    RequiredColumns=["trade_id", "customer_id", "amount"],
    TargetClass=Trade,
)

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