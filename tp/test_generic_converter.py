import pandas as pd
import common_include as C
from typing import Any, get_type_hints


@C.dataclass
class BaseRowModel(C.BaseObject):
    @classmethod
    def from_value(cls, value):
        """
        Default implementation.

        Most subclasses won't need to override this.
        """
        return cls(value)

    # @classmethod
    # def from_dict(cls, d: dict):
    #     field_types = get_type_hints(cls)
    #     mapped = {}
    #
    #     for field_name, field_type in field_types.items():
    #         raw_value = d.get(field_name, None)
    #         mapped[field_name] = cls._to_type(raw_value, field_type)
    #
    #     return cls(**mapped)

    @staticmethod
    def _to_type(value, target_type):

        if value is None or pd.isna(value):
            return None

        if hasattr(target_type, "from_value"):
            return target_type.from_value(value)

        return value
    # @classmethod
    # def from_dict(cls, d: dict):
    #     field_types = get_type_hints(cls)
    #     mapped = {}
    #
    #     for field_name, field_type in field_types.items():
    #         raw_value = d.get(field_name, None)
    #         mapped[field_name] = cls._to_type(raw_value, field_type)
    #
    #     return cls(**mapped)

    @staticmethod
    def _to_type_1(value, target_type):
        if value is None or pd.isna(value):
            return None

        if target_type == str:
            return str(value).strip()

        if target_type == int:
            return int(str(value).replace(",", "").strip())

        if target_type == float:
            return float(
                str(value)
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

        if target_type == bool:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in ("true", "1", "yes", "y")

        # custom app/base types
        if hasattr(target_type, "from_value"):
            x = target_type.from_value(value)
            return x

        # fallback: try constructor
        try:
            return target_type(value)
        except Exception:
            return value

def df_to_class_list(df: pd.DataFrame, target_class: type) -> list:
    records = df.to_dict(orient="records")
    x = [target_class.from_dict(row) for row in records]
    return x

@C.dataclass
class Trade(BaseRowModel):
    customer_id: int = None
    amount: float = None
    trade_id: str = None
    Symbol: C.BaseTradeSymbol = None




if __name__ == "__main__":
    test_data = [
        {"trade_id": "AAAA", "customer_id": 100, "amount": "$50", "Symbol": "TEST"},
        {"trade_id": "BBBB", "customer_id": 200, "amount": "$20", "Symbol": "TEST2"},

    ]

    # df = pd.DataFrame(test_data)
    df = pd.DataFrame({
        "trade_id": ["AAAA", "BBBB"],
        "customer_id": [100, 200],
        "amount": ["$50", "$20"],
        "Symbol": ["TEST", "TEST2"]
    })

    print(df)
    trades = df_to_class_list(df, Trade)
    print(trades)
