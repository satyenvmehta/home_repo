# def delete_col(df, col_name):
import os

from base_lib.core.common_include import *
import pandas as pd

from base_lib.core.base_include import *


@dataclass
class PandasUtil(BaseObject):
    dirName : BaseString
    fileName : BaseString
    df : DataFrame = None

    def __post_init__(self):
        self.setFileName()
        self.load()
        return

    def setFileName(self):  #, file_path, file_name):
        self.cvs_file = os.path.join(self.dirName, self.fileName)
        return

    def load(self):
        self.df =  pd.read_csv(self.cvs_file)
        return

    def info(self):
        if not self.df.empty:
            self.df.info()
            self.df.head(5)
            print(self.df["ocean_proximity"].value_counts())
            print(self.df.describe())
        return

    def draw(self):
        x = self.df.hist(bins=50, figsize=(11, 8))
        return

    def reset(self):
        self.df.reset_index()
        return

dirName = 'C:\\Users\\Consultant\\Downloads'
fileName = 'housing.csv'
histfile = 'all_history.csv'

def ut_history():
    pu = PandasUtil(dirName, histfile)

if __name__ == '__main__':
    pu = PandasUtil(dirName, fileName)
    # pu.load()
    pu.info()
    pu.draw()
