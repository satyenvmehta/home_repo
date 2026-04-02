import common_include as C
import pandas as pd

from datetime import datetime
from typing import Any, Optional


@C.dataclass
class BaseETLObject(C.BaseObject):
    pass


@C.dataclass
class ETLError(BaseETLObject):
    Step: str
    Message: str

    def __str__(self) -> str:
        return f"[{self.Step}] {self.Message}"


@C.dataclass
class LoadResult(BaseETLObject):
    Name: str
    LoadType: str
    RawData: Any = None
    PreparedData: Optional[pd.DataFrame] = None
    ObjectList: Optional[list] = None
    RowCount: int = 0
    IsValid: bool = False
    Errors: list = C.field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.Errors.append(ETLError(Step=step, Message=message))

    @property
    def HasErrors(self) -> bool:
        return len(self.Errors) > 0


@C.dataclass
class TransformResult(BaseETLObject):
    Name: str
    OutputData: Optional[pd.DataFrame] = None
    RowCount: int = 0
    IsValid: bool = False
    Errors: list = C.field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.Errors.append(ETLError(Step=step, Message=message))

    @property
    def HasErrors(self) -> bool:
        return len(self.Errors) > 0


@C.dataclass
class ExtractResult(BaseETLObject):
    Name: str
    Outputs: dict = C.field(default_factory=dict)
    IsValid: bool = False
    Errors: list = C.field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.Errors.append(ETLError(Step=step, Message=message))

    @property
    def HasErrors(self) -> bool:
        return len(self.Errors) > 0


@C.dataclass
class ETLContext(BaseETLObject):
    RefData: dict = C.field(default_factory=dict)
    MainData: dict = C.field(default_factory=dict)

    RefObjects: dict = C.field(default_factory=dict)
    MainObjects: dict = C.field(default_factory=dict)

    DerivedData: dict = C.field(default_factory=dict)
    ExtractData: dict = C.field(default_factory=dict)

    TransformedData: Optional[pd.DataFrame] = None

    def get_ref_data(self, name: str) -> pd.DataFrame:
        if name not in self.RefData:
            raise KeyError(f"Reference data not found: {name}")
        return self.RefData[name]

    def get_main_data(self, name: str) -> pd.DataFrame:
        if name not in self.MainData:
            raise KeyError(f"Main data not found: {name}")
        return self.MainData[name]


@C.dataclass
class StepAudit(BaseETLObject):
    StepName: str
    StartTs: datetime = C.field(default_factory=datetime.now)
    EndTs: Optional[datetime] = None
    Status: str = "STARTED"
    RowCount: int = 0
    Details: dict = C.field(default_factory=dict)

    def complete(self, status: str = "SUCCESS", row_count: int = 0, **kwargs) -> None:
        self.EndTs = datetime.now()
        self.Status = status
        self.RowCount = row_count
        self.Details.update(kwargs)


@C.dataclass
class ETLReport(BaseETLObject):
    EtlName: str
    Audits: list = C.field(default_factory=list)
    Errors: list = C.field(default_factory=list)

    def add_audit(self, audit: StepAudit) -> None:
        self.Audits.append(audit)

    def add_error(self, step: str, message: str) -> None:
        self.Errors.append(ETLError(Step=step, Message=message))

    @property
    def IsSuccess(self) -> bool:
        return len(self.Errors) == 0