from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


# ============================================================
# Common Models
# ============================================================

@dataclass
class ETLError:
    step: str
    message: str

    def __str__(self) -> str:
        return f"[{self.step}] {self.message}"


@dataclass
class StepAudit:
    step_name: str
    start_ts: datetime = field(default_factory=datetime.now)
    end_ts: Optional[datetime] = None
    status: str = "STARTED"
    row_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def complete(self, status: str = "SUCCESS", row_count: int = 0, **kwargs) -> None:
        self.end_ts = datetime.now()
        self.status = status
        self.row_count = row_count
        self.details.update(kwargs)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.end_ts is None:
            return None
        return (self.end_ts - self.start_ts).total_seconds()


@dataclass
class LoadResult:
    name: str
    load_type: str
    raw_data: Any = None
    prepared_data: Optional[pd.DataFrame] = None
    row_count: int = 0
    is_valid: bool = False
    errors: List[ETLError] = field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(ETLError(step=step, message=message))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class TransformResult:
    name: str
    output_data: Optional[pd.DataFrame] = None
    row_count: int = 0
    is_valid: bool = False
    errors: List[ETLError] = field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(ETLError(step=step, message=message))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class ExtractResult:
    name: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = False
    errors: List[ETLError] = field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(ETLError(step=step, message=message))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class ETLContext:
    ref_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    main_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    derived_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    transformed_data: Optional[pd.DataFrame] = None
    extract_data: Dict[str, Any] = field(default_factory=dict)

    def get_ref(self, name: str) -> pd.DataFrame:
        if name not in self.ref_data:
            raise KeyError(f"Reference data '{name}' not found")
        return self.ref_data[name]

    def get_main(self, name: str) -> pd.DataFrame:
        if name not in self.main_data:
            raise KeyError(f"Main data '{name}' not found")
        return self.main_data[name]

    def get_derived(self, name: str) -> pd.DataFrame:
        if name not in self.derived_data:
            raise KeyError(f"Derived data '{name}' not found")
        return self.derived_data[name]


@dataclass
class ETLReport:
    etl_name: str
    audits: List[StepAudit] = field(default_factory=list)
    errors: List[ETLError] = field(default_factory=list)

    def add_audit(self, audit: StepAudit) -> None:
        self.audits.append(audit)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(ETLError(step=step, message=message))

    @property
    def is_success(self) -> bool:
        return len(self.errors) == 0


# ============================================================
# BaseLoad
# ============================================================

@dataclass
class BaseLoad(ABC):
    name: str
    required_columns: List[str] = field(default_factory=list)
    load_type: str = "main"   # ref or main

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

        result.prepared_data = prepared_df
        result.row_count = len(prepared_df)
        result.is_valid = True
        return result

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


# ============================================================
# Concrete Loads
# ============================================================

@dataclass
class DataFrameLoad(BaseLoad):
    source_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    def load_raw(self) -> Any:
        return self.source_df.copy()

    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        df = raw_data.copy()
        df.columns = [str(col).strip() for col in df.columns]
        return df


@dataclass
class CSVLoad(BaseLoad):
    file_path: str = ""
    read_csv_kwargs: Dict[str, Any] = field(default_factory=dict)

    def load_raw(self) -> Any:
        return pd.read_csv(self.file_path, **self.read_csv_kwargs)

    def create_prepared(self, raw_data: Any) -> pd.DataFrame:
        df = raw_data.copy()
        df.columns = [str(col).strip() for col in df.columns]
        return df
