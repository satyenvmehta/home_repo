from __future__ import annotations

from dataclasses import dataclass, field
# from pathlib import Path
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Optional, Union, Iterable, Iterator, Sequence, Mapping, Callable, TypeVar, Generic

def date_now(fmt="%Y-%m-%d %H:%M"):
    return datetime.now().strftime(fmt)

__all__ = [
    "dataclass", "field",
    # "Path",
    "date", "datetime", "time", "timedelta", "timezone",
    "Any", "Optional", "Union",
    "Iterable", "Iterator", "Sequence", "Mapping",
    "Callable", "TypeVar", "Generic",
    "date_now"
]
