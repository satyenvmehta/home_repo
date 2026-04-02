from __future__ import annotations

import common_include as C
import pandas as pd

from abc import ABC, abstractmethod
from typing import Any, Optional

from base_lib.etl.base_etl import BaseETLObject, LoadResult


@C.dataclass
class BaseLoad(BaseETLObject, ABC):
    Name: str
    RequiredColumns: list = C.field(default_factory=list)
    LoadType: str = "main"
    TargetClass: Optional[type] = None
    ObjectList: Optional[list] = None

    def run(self) -> LoadResult:
        result = LoadResult(Name=self.Name, LoadType=self.LoadType)

        raw_data = self.load_raw()
        result.RawData = raw_data

        self.validate_raw(raw_data=raw_data, result=result)
        if result.HasErrors:
            return result

        prepared_df = self.create_prepared(raw_data=raw_data)
        self.validate_prepared(df=prepared_df, result=result)
        if result.HasErrors:
            return result

        if self.TargetClass is not None:
            object_list = self.convert_to_objects(df=prepared_df, result=result)
            if result.HasErrors:
                return result

            self.validate_objects(object_list=object_list, result=result)
            if result.HasErrors:
                return result

            self.ObjectList = object_list
            result.ObjectList = object_list

        result.PreparedData = prepared_df
        result.RowCount = len(prepared_df)
        result.IsValid = True
        return result

    @abstractmethod
    def load_raw(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        raise NotImplementedError

    def validate_raw(self, raw_data: Any, result: LoadResult) -> None:
        if raw_data is None:
            result.add_error("validate_raw", f"{self.Name}: raw data is None")

    def validate_prepared(self, df: pd.DataFrame, result: LoadResult) -> None:
        if df is None:
            result.add_error("validate_prepared", f"{self.Name}: prepared data is None")
            return
        if not isinstance(df, pd.DataFrame):
            result.add_error("validate_prepared", f"{self.Name}: prepared data must be pandas DataFrame")
            return

        missing_cols = [col for col in self.RequiredColumns if col not in df.columns]
        if missing_cols:
            result.add_error("validate_prepared", f"{self.Name}: missing required columns: {missing_cols}")

    def convert_to_objects(self, df: pd.DataFrame, result: LoadResult) -> list:
        object_list = []

        if not hasattr(self.TargetClass, "from_dict"):
            result.add_error("convert_to_objects", f"{self.Name}: TargetClass does not support from_dict")
            return object_list

        rows = df.to_dict(orient="records")
        for i, row in enumerate(rows):
            try:
                obj = self.TargetClass.from_dict(row)
                object_list.append(obj)
            except Exception as ex:
                result.add_error("convert_to_objects", f"{self.Name}: row {i} conversion failed: {str(ex)}")

        return object_list

    def validate_objects(self, object_list: list, result: LoadResult) -> None:
        if len(object_list) == 0:
            result.add_error("validate_objects", f"{self.Name}: no objects created")


@C.dataclass
class DataFrameLoad(BaseLoad):
    SourceDf: Optional[pd.DataFrame] = None

    def load_raw(self) -> Any:
        if self.SourceDf is None:
            return None
        return self.SourceDf.copy()

    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        df = raw_data.copy()
        df.columns = [str(col).strip() for col in df.columns]
        return df


@C.dataclass
class CSVLoad(BaseLoad):
    FilePath: str = ""
    ReadCsvKwargs: dict = C.field(default_factory=dict)

    def load_raw(self) -> Any:
        return pd.read_csv(self.FilePath, **self.ReadCsvKwargs)

    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        df = raw_data.copy()
        df.columns = [str(col).strip() for col in df.columns]
        return df