from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ---------------------------------------
# Base object (NOT a dataclass, NOT frozen)
# ---------------------------------------
class BaseObject:
    def print(self, indent: int = 0) -> None:
        pad = " " * indent
        print(f"{pad}{self}")


# ---------------------------------------
# Primitive value types (FROZEN)
# ---------------------------------------
@dataclass(frozen=True)
class BaseInt(BaseObject):
    value: int = 0

    def __str__(self) -> str:
        return f"Int({self.value})"


@dataclass(frozen=True)
class BaseStr(BaseObject):
    value: str = ""

    def __str__(self) -> str:
        return f"Str('{self.value}')"


@dataclass(frozen=True)
class BaseFloat(BaseObject):
    value: float = 0.0

    def __str__(self) -> str:
        return f"Float({self.value})"


@dataclass(frozen=True)
class BaseBool(BaseObject):
    value: bool = False

    def __str__(self) -> str:
        return f"Bool({self.value})"


# ---------------------------------------
# Base Container (UNIVERSAL PRINT + ADD)
# ---------------------------------------
@dataclass
class BaseContainer(BaseObject):

    def _print_item(self, item, indent: int) -> None:
        """Recursive printer for items."""
        if isinstance(item, BaseObject):
            item.print(indent)
        else:
            pad = " " * indent
            print(f"{pad}{item!r}")

    def print(self, indent: int = 0) -> None:
        """Generic container printer — works for ALL containers."""
        pad = " " * indent
        print(f"{pad}{self}")  # uses derived __str__()

        for key, val in self._iter_items():
            label = f"{key!r}" if key is not None else "•"
            print(f"{pad}  {label} →")
            self._print_item(val, indent + 6)

    def _iter_items(self):
        """
        To be overridden by subclasses.
        Must yield (key, value) pairs.
        For containers without a key (like sets / optionals),
        use key = None.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must override _iter_items()")

    # ---------- Generic add API ----------
    def add(self, *args, **kwargs):
        """
        Public method to add/append items to this container.
        Semantics depend on the concrete subclass.
        """
        return self._add(*args, **kwargs)

    def _add(self, *args, **kwargs):
        """
        To be overridden by subclasses.
        Implementation of container-specific add/append.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must override _add()")


# ---------------------------------------
# BaseKeyValue
# ---------------------------------------
@dataclass
class BaseKeyValue(BaseObject):
    key: BaseObject | object
    value: BaseObject | object

    def __post_init__(self):
        # Normalize key: ensure it's a BaseObject (default = BaseStr)
        if not isinstance(self.key, BaseObject):
            self.key = BaseStr(str(self.key))

        # For value we *don't* force wrapping yet (design choice for now).
        # You *can* add auto-wrapping logic later if you like.

    def __str__(self) -> str:
        return f"KeyValue({self.key} -> {self.value})"


# ---------------------------------------
# BaseList
# ---------------------------------------
@dataclass
class BaseList(BaseContainer):
    items: list | None = None

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = []

    def __str__(self) -> str:
        return f"List(len={len(self.items)})"

    def _iter_items(self):
        for i, x in enumerate(self.items):
            yield i, x

    def _add(self, value):
        """Append an item to the list."""
        self.items.append(value)
        return self  # allow chaining


# ---------------------------------------
# BaseDict  (HYBRID + uses BaseKeyValue)
# ---------------------------------------
@dataclass
class BaseDict(BaseContainer):
    # Hybrid:
    # - User can pass dict
    # - Or list[BaseKeyValue]
    # - Or list[(key, value)]
    items: list[BaseKeyValue] | dict | None = None

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = []

        elif isinstance(self.items, dict):
            # dict → list[BaseKeyValue], let BaseKeyValue normalize keys
            self.items = [BaseKeyValue(k, v) for k, v in self.items.items()]

        else:
            # Assume iterable of BaseKeyValue or (key, value)
            converted: list[BaseKeyValue] = []
            for item in self.items:
                if isinstance(item, BaseKeyValue):
                    converted.append(item)
                elif isinstance(item, tuple) and len(item) == 2:
                    k, v = item
                    converted.append(BaseKeyValue(k, v))
                else:
                    raise TypeError(
                        "BaseDict items must be dict, list[BaseKeyValue], "
                        "or list[(key, value)]"
                    )
            self.items = converted

    def __str__(self) -> str:
        return f"Dict(len={len(self.items)})"

    def _iter_items(self):
        # Expose (key, value) to BaseContainer.print()
        for kv in self.items:
            yield kv.key, kv.value

    def _add(self, key, value=None):
        """
        Flexible add:
          - add(BaseKeyValue(...))
          - add((key, value))
          - add(key, value)
        """
        if isinstance(key, BaseKeyValue) and value is None:
            self.items.append(key)
        elif value is None and isinstance(key, tuple) and len(key) == 2:
            k, v = key
            self.items.append(BaseKeyValue(k, v))
        else:
            # treat as (key, value)
            self.items.append(BaseKeyValue(key, value))
        return self


# ---------------------------------------
# BaseSet
# ---------------------------------------
@dataclass
class BaseSet(BaseContainer):
    items: set | None = None

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = set()

    def __str__(self) -> str:
        return f"Set(len={len(self.items)})"

    def _iter_items(self):
        for x in self.items:
            yield None, x

    def _add(self, value):
        """Add an item to the set."""
        self.items.add(value)
        return self


# ---------------------------------------
# BaseTuple
# ---------------------------------------
@dataclass
class BaseTuple(BaseContainer):
    items: tuple | None = None

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = ()
        elif not isinstance(self.items, tuple):
            self.items = tuple(self.items)

    def __str__(self) -> str:
        return f"Tuple(len={len(self.items)})"

    def _iter_items(self):
        for i, x in enumerate(self.items):
            yield i, x

    def _add(self, value):
        """Append logically by creating a new tuple."""
        self.items = (*self.items, value)
        return self


# ---------------------------------------
# BaseOptional
# ---------------------------------------
@dataclass
class BaseOptional(BaseContainer):
    value: BaseObject | None = None

    def __str__(self) -> str:
        if self.value is None:
            return "Optional(None)"
        return "Optional(Some)"

    def _iter_items(self):
        if self.value is not None:
            yield None, self.value

    def _add(self, value):
        """Set/replace the optional value."""
        self.value = value
        return self


# ---------------------------------------
# BaseEnum + example Enum type
# ---------------------------------------
@dataclass(frozen=True)
class BaseEnum(BaseObject):
    value: Enum

    def __str__(self) -> str:
        enum_type = self.value.__class__.__name__
        return f"Enum({enum_type}.{self.value.name})"


class Color(Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"


# ---------------------------------------
# Example usage
# ---------------------------------------
if __name__ == "__main__":
    # Primitive values
    i = BaseInt(10)
    s = BaseStr("hello")
    f = BaseFloat(3.14)
    b = BaseBool(True)

    # List with add()
    lst = BaseList()
    lst.add(i).add(s).add(f)

    # Dict using HYBRID input (plain dict)
    dct = BaseDict({"flag": b, "num": i})
    dct.add("extra", BaseStr("twenty-five"))

    # Dict using list of (k, v)
    dct2 = BaseDict([("name", "Satyen"), ("age", BaseInt(25))])
    dct2.add(("country", BaseStr("USA")))

    # Dict using explicit BaseKeyValue
    kv1 = BaseKeyValue("city", BaseStr("Dayton"))
    kv2 = BaseKeyValue(BaseStr("state"), BaseStr("NJ"))
    dct3 = BaseDict([kv1, kv2])
    dct3.add(BaseKeyValue("zip", BaseInt(8852)))
    dct3.add(("country", BaseStr("USA")))
    dct3.add(("Marks", 100))

    # Set, Tuple, Optional, Enum
    st = BaseSet()
    st.add(BaseStr("a")).add(BaseStr("b"))

    tpl = BaseTuple()
    tpl.add(i).add(b).add(BaseStr("tuple-item"))

    opt1 = BaseOptional()
    opt2 = BaseOptional().add(BaseStr("optional value"))

    color_enum = BaseEnum(Color.GREEN)

    print("\n--- BaseList ---")
    lst.print()

    print("\n--- BaseDict (from dict + add) ---")
    dct.print()

    print("\n--- BaseDict (from list of tuples + add) ---")
    dct2.print()

    print("\n--- BaseDict (from BaseKeyValue list + add) ---")
    dct3.print()

    print("\n--- BaseSet ---")
    st.print()

    print("\n--- BaseTuple ---")
    tpl.print()

    print("\n--- BaseOptional(None) ---")
    opt1.print()

    print("\n--- BaseOptional(Some) ---")
    opt2.print()

    print("\n--- BaseEnum ---")
    color_enum.print()
