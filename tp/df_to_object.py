from common_include import *

class Reading:
    def __init__(self, h, p, q):
        self.HourOfDay = h
        self.Percentage = p
        self.col3 = q
        return
def reading_list(df:pd.DataFrame)->list:
    return list(map(lambda x:Reading(x[0], x[1], x[2]),df.values.tolist()))

@dataclass
class Reading2:
    HourOfDay: any
    col2: any
    col3: any

def reading_list2(df:pd.DataFrame)->list:

    return list(map(lambda x:Reading2(x[0], x[1], x[2]),df.values.tolist()))

if __name__ == '__main__':
    technologies = [["Spark", 20000, "30days"],
                    ["pandas", 20000, "40days"],
                    ]
    df = pd.DataFrame(technologies)
    print(df)

    res = reading_list(df)
    print(res[1].col3)


    res2 = reading_list2(df)
    print(res2[1].col3)