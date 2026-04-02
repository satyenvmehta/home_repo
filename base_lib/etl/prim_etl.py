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

    ref_objects: Dict[str, List[Any]] = field(default_factory=dict)
    main_objects: Dict[str, List[Any]] = field(default_factory=dict)

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



# ============================================================
# BaseETL
# ============================================================

@dataclass
class BaseETL:
    name: str
    ref_loads: Dict[str, BaseLoad] = field(default_factory=dict)
    main_loads: Dict[str, BaseLoad] = field(default_factory=dict)
    # transformer: Optional[BaseTransform] = None
    # extractor: Optional[BaseExtract] = None
    context: ETLContext = field(default_factory=ETLContext)
    report: ETLReport = field(init=False)

    def __post_init__(self) -> None:
        self.report = ETLReport(etl_name=self.name)

    def add_ref_load(self, load: BaseLoad) -> None:
        load.load_type = "ref"
        self.ref_loads[load.name] = load

    def add_main_load(self, load: BaseLoad) -> None:
        load.load_type = "main"
        self.main_loads[load.name] = load

    # def set_transformer(self, transformer: BaseTransform) -> None:
    #     self.transformer = transformer
    #
    # def set_extractor(self, extractor: BaseExtract) -> None:
    #     self.extractor = extractor

    def run(self) -> ETLContext:
        self.run_loads()
        self.run_transform()
        self.run_extract()
        return self.context

    def run_loads(self) -> None:
        self._run_load_group(loads=self.ref_loads, target_dict=self.context.ref_data, group_name="reference_loads")
        self._run_load_group(loads=self.main_loads, target_dict=self.context.main_data, group_name="main_loads")

    def _run_load_group(
        self,
        loads: Dict[str, BaseLoad],
        target_dict: Dict[str, pd.DataFrame],
        group_name: str,
    ) -> None:
        for load_name, load_obj in loads.items():
            audit = StepAudit(step_name=f"{group_name}.{load_name}")

            try:
                result = load_obj.run()
                if not result.is_valid:
                    for error in result.errors:
                        self.report.add_error(error.step, error.message)
                    audit.complete(status="FAILED")
                    self.report.add_audit(audit)
                    raise ValueError(f"Load failed: {load_name}")

                target_dict[load_name] = result.prepared_data
                if load_obj.target_class and load_obj.object_list:
                    if load_obj.load_type == "ref":
                        self.context.ref_objects[load_name] = load_obj.object_list
                    else:
                        self.context.main_objects[load_name] = load_obj.object_list
                audit.complete(status="SUCCESS", row_count=result.row_count)

            except Exception as ex:
                if audit.status != "FAILED":
                    audit.complete(status="FAILED")
                self.report.add_error(group_name, f"{load_name}: {str(ex)}")
                self.report.add_audit(audit)
                raise

            self.report.add_audit(audit)

    def run_transform(self) -> None:
        if self.transformer is None:
            raise ValueError("Transformer is not configured")

        audit = StepAudit(step_name=f"transform.{self.transformer.name}")

        try:
            result = self.transformer.run(self.context)
            if not result.is_valid:
                for error in result.errors:
                    self.report.add_error(error.step, error.message)
                audit.complete(status="FAILED")
                self.report.add_audit(audit)
                raise ValueError(f"Transform failed: {self.transformer.name}")

            self.context.transformed_data = result.output_data
            audit.complete(status="SUCCESS", row_count=result.row_count)

        except Exception as ex:
            if audit.status != "FAILED":
                audit.complete(status="FAILED")
            self.report.add_error("transform", str(ex))
            self.report.add_audit(audit)
            raise

        self.report.add_audit(audit)

    def run_extract(self) -> None:
        if self.extractor is None:
            raise ValueError("Extractor is not configured")

        audit = StepAudit(step_name=f"extract.{self.extractor.name}")

        try:
            result = self.extractor.run(self.context)
            if not result.is_valid:
                for error in result.errors:
                    self.report.add_error(error.step, error.message)
                audit.complete(status="FAILED")
                self.report.add_audit(audit)
                raise ValueError(f"Extract failed: {self.extractor.name}")

            self.context.extract_data.update(result.outputs)
            audit.complete(status="SUCCESS", row_count=0)

        except Exception as ex:
            if audit.status != "FAILED":
                audit.complete(status="FAILED")
            self.report.add_error("extract", str(ex))
            self.report.add_audit(audit)
            raise

        self.report.add_audit(audit)