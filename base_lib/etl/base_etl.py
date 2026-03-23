import pandas as pd

import common_include as C


@C.dataclass
class Error(C.BaseObject):
    step: C.BaseString
    message: C.BaseString

    def __str__(self) -> str:
        return f"[{self.step.getBase()}] {self.message.getBase()}"


from abc import ABC, abstractmethod

@C.dataclass
class BaseLoad(C.BaseString)


@C.dataclass
class BaseETL(C.BaseObject):
    references: C.BaseList
    loads: C.BaseList
    extracts: C.BaseList

    def __post_init__(self):
        return
    def validate_loads(self):
        for ref in self.references:
            if ref.
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

class Bhavferi(BaseETL):

