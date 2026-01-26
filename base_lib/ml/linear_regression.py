from base_lib.core.PANDAS_UTILS import PandasUtil
# from base_lib.core.common_include import *
from base_lib.core.base_include import *

from ml.model import MLModel


dirName = 'C:\\Users\\Consultant\\Downloads'
fileName = 'housing.csv'

@dataclass
class LinearRegressionModel(MLModel):
    dirName : BaseString
    fileName : BaseString
    # data : any = None
    # graph : any = None

    def __post_init__(self):
        self.pre_process_data()
        return

    def pre_process_data(self):
        self.data = PandasUtil(self.dirName, self.fileName)
        return

    def view_sample(self):
        self.data.info()
        return

    def train_model(self):
        pass

    def evaluate(self, test_data, test_target):
        pass

if __name__ == '__main__':

    dirName = 'C:\\Users\\Consultant\\Downloads'
    fileName = 'housing.csv'
    lr_inst = LinearRegressionModel(dirName, fileName)
    lr_inst.view_sample()

    # pu = PandasUtil(dirName, fileName)
    # pu.info()
    # gu = GraphicsUtil()
    # gu.plot_all(pu.df)
