import os
import sys

print(sys.path)

import sys
def setpath():
    thisdir = 'C:/Users/Consultant/PycharmProjects/baselib'
    sys.path.append(thisdir)


from datetime import date

def Today(format="%m/%d/%Y"):
    today = date.today()
    return today.strftime(format)

def getPwd():
    return os.getcwd()

if __name__ == '__main__':
    print(Today('%b-%d'))