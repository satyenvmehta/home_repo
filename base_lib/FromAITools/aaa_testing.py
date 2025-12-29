
from all_include import *

@dataclass
class _MyInteger(int):  # Assuming OtherClass is defined elsewhere
    def __new__(cls, value):
        # You can implement custom behavior here if needed
        # return int.__new__(cls, value)
        # return int.__new__(cls, value)

        val = super().__new__(int, value)
        # val = BaseObject.__post_init__(val)

        # val = int.__new__(value)

        # BaseObject.setBase(val)

        return val

    # You can define additional methods and override existing ones here

class MyInteger(_MyInteger, BaseObject):
    pass

# Example usage:
num = MyInteger(5)

print(num)
print(num.getBase())
