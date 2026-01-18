# from common_include import *

import pandas as pd

@dataclass
class FileObject(object):
    item : Any
    df: Any = field(init=False)

    def read(self, index_col=None, skip=0):
        self.df = pd.read_csv(self.item, index_col=index_col, skiprows=skip)
        return self.df

        # self.fh = open(self.item)
        #
        # with open(self.item) as self.fh:
        #     csv_reader = csv.reader(self.fh, delimiter=',')
        #     line_count = 0
        #     for row in csv_reader:
        #         if line_count < skip:
        #             line_count = line_count+1
        #             continue
        #         if line_count == skip:
        #             self.header = row
        #         else:
        #             self.info.append(row)

if __name__ == '__main__':
    fo = FileObject('abc')
    fo.read()