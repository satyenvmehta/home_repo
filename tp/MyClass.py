# MyClass.py

from base_lib.core.common_include import  unittest

# unittest = False  # Default value

class MyClass:
    def __init__(self, value):
        self.value = value

    def display(self):
        print(f"Value: {self.value}, {unittest}")
        if unittest:
            print("Unittest in progress")

m = MyClass(10)

# unittest = True
m.display()