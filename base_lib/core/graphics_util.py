import os
from dataclasses import dataclass

from common_include import *

import matplotlib.pyplot as plt

from base_lib.core.PANDAS_UTILS import PandasUtil
from base_lib.core.base_classes import BaseObject


import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# Where to save the figures
PROJECT_ROOT_DIR = 'C:\\Users\\Consultant\\Downloads'
CHAPTER_ID = "end_to_end_project"

# def save_fig(fig_id, tight_layout=True):
#     path = os.path.join(PROJECT_ROOT_DIR, "images", CHAPTER_ID, fig_id + ".png")
#     print("Saving figure", fig_id)
#     if tight_layout:
#         plt.tight_layout()
#     plt.savefig(path, format='png', dpi=300)
#     return

@dataclass
class GraphicsUtil(BaseObject):
    df : DataFrame = None

    def plot_all(self, df):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        df.hist('longitude', ax=ax)
        # df.hist(bins=50, figsize=(11, 8))
        path = os.path.join(PROJECT_ROOT_DIR,  'test28' + ".png")
        fig.savefig(path)
        # plt.savefig(path, format='png', dpi=300)
        print("Saved in " + path)

dirName = 'C:\\Users\\Consultant\\Downloads'
fileName = 'housing.csv'
if __name__ == '__main__':
    pu = PandasUtil(dirName, fileName)
    pu.info()
    gu = GraphicsUtil()
    gu.plot_all(pu.df)
