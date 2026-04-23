import pandas as pd

import common_include as C


@C.dataclass
class Error(C.BaseObject):
    step: C.BaseString
    message: C.BaseString

    def __str__(self) -> str:
        return f"[{self.step.getBase()}] {self.message.getBase()}"


# from abc import ABC, abstractmethod

@C.dataclass
class ETLError:
    step: C.BaseString
    message: C.BaseString

    def __str__(self) -> str:
        return f"[{self.step}] {self.message}"

@C.dataclass
class LoadResult:
    name: str
    load_type: str
    raw_data: C.Any = None
    prepared_data: Optional[pd.DataFrame] = None
    row_count: int = 0
    is_valid: bool = False
    errors: List[ETLError] = field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(ETLError(step=step, message=message))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

# ============================================================
# BaseLoad
# ============================================================

@C.dataclass
class BaseLoad(C.ABC):
    name: C.BaseString
    required_columns: C.BaseList[C.BaseString] = C.field(default_factory=list)
    load_type: C.BaseString = "main"   # ref or main

    target_class: Optional[type] = None
    object_list: Optional[List[Any]] = field(default=None, init=False)

    def run(self) -> LoadResult:
        result = LoadResult(name=self.name, load_type=self.load_type)

        raw_data = self.load_raw()
        result.raw_data = raw_data

        self.validate_raw(raw_data, result)
        if result.has_errors:
            return result

        prepared_df = self.create_prepared(raw_data)
        self.validate_prepared(prepared_df, result)
        if result.has_errors:
            return result

        if self.target_class:
            obj_list = self.convert_to_objects(prepared_df, result)
            if result.has_errors:
                return result

            self.object_list = obj_list
            self.validate_objects(obj_list, result)
            if result.has_errors:
                return result

        result.prepared_data = prepared_df
        result.row_count = len(prepared_df)
        result.is_valid = True
        return result

    def convert_to_objects(
            self,
            df: pd.DataFrame,
            result: LoadResult
    ) -> List[Any]:
        objects = []

        try:
            records = df.to_dict(orient="records")

            for idx, rec in enumerate(records):
                try:
                    # if isinstance(self.target_class, type):
                    obj = self.target_class.from_dict(rec)
                    objects.append(obj)
                except Exception as ex:
                    result.add_error(
                        "convert_to_objects",
                        f"{self.name}: row {idx} failed: {str(ex)}"
                    )

        except Exception as ex:
            result.add_error("convert_to_objects", str(ex))

        return objects

    def validate_objects(
            self,
            objects: List[Any],
            result: LoadResult
    ) -> None:
        if not objects:
            result.add_error("validate_objects", f"{self.name}: no objects created")

    @abstractmethod
    def load_raw(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        raise NotImplementedError

    def validate_raw(self, raw_data: Any, result: LoadResult) -> None:
        if raw_data is None:
            result.add_error("validate_raw", f"{self.name}: raw data is None")

    def validate_prepared(self, df: pd.DataFrame, result: LoadResult) -> None:
        if df is None:
            result.add_error("validate_prepared", f"{self.name}: prepared data is None")
            return

        if not isinstance(df, pd.DataFrame):
            result.add_error("validate_prepared", f"{self.name}: prepared data must be DataFrame")
            return

        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            result.add_error(
                "validate_prepared",
                f"{self.name}: missing required columns {missing_cols}"
            )


@C.dataclass
class BaseETL(C.BaseObject):
    references: C.BaseList
    loads: C.BaseList
    extracts: C.BaseList

    def __post_init__(self):
        return
    # def validate_loads(self):
    #     for ref in self.references:
    #         if ref.
    def load(self):
        return
    def transform(self):
        return
    def extract(self):
        return

    def etl(self):
        self.load()
        self.extract()
        self.load()
        return

# class Bhavferi(BaseETL):
#
