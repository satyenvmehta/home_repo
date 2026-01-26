# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# from math import hex2float

import sys

from base_lib.core.base_classes import BaseBool


def append_path(path):
    sys.path.append(path)
    return None

import math_utils

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# from  base_include import BaseBool

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    from base_lib.core.files_include import output_file
    print(output_file)
    print_hi('PyCharm1')
    # thisdir = 'C:/Users/Consultant/PycharmProjects/baselib'
    # append_path(thisdir)
    print(math_utils.hex2float('A'))
    b = BaseBool(True)
    print(b.getBase())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
