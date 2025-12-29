# from common_include import *
# import pandas as pd
from pprint import pprint

# def insert_lib():
#     import os
#     import sys
#     base_lib = r'G:\My Drive\Software\PycharmProjects\base_lib'
#     base_lib = r'G:\My Drive\Software\PycharmProjects\base_lib'
#     sys.path.append(base_lib)
#     # os.environ['PYTHONPATH'] = base_lib + os.pathsep + os.environ.get('PYTHONPATH', '')
#     return
#
# insert_lib()

# def test_save_file():
#     listOfInterest = {'Results': []}
#     b._saveResults(listOfInterest=listOfInterest, fileName=output_file, altFilename=alt_output_file)
#     exit(1)
#
from base_lib.core.files_include import output_file, alt_output_file


def test_save_file(b):
    listOfInterest = {'Results': []}
    b._saveResults(listOfInterest=listOfInterest, fileName=output_file, altFilename=alt_output_file)
    exit(1)

def tp():
    print(output_file)
    b =  BaseLib()
    test_save_file()
    print("Done..")
if __name__ == '__main__':
    tp()


