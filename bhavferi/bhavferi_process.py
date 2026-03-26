
import pandas as pd

import common_include as C

@C.dataclass
class BhavferiProcessing(C.BaseClass):
    datafile_name : C.BaseString
    reference_names : C.BaseString
    street_names: C.BaseString
    zipcodes : C.BaseList

    