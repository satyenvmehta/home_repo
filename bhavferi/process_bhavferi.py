from __future__ import annotations

import common_include as C
from base_lib.core.Person import Person
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


@C.dataclass
class Person(C.BaseObject):
    Address: str = None
    Name: str = None

load_csv = CSVLoad(
    Name="Monroe",
    FilePath="Monroe_QA.txt",
    fld_sep = "\t",
    LoadType="main",
    TargetClass=Person,
    RequiredColumns=["Address", "Name"],
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


if __name__ == "__main__":
    # run_load(load=load)
    run_load(load=load_csv)