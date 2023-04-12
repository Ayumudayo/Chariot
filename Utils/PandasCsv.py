import os
import pandas as pd


class pdCsv:

    def __init__(self):
        super().__init__()
        pdCsv.addr = ''
        pdCsv.csv = None
    

    def load_csv(guild_id):
        pdCsv.addr = f'./results/{guild_id}.csv'

        if(not os.path.exists('./results')):
            os.mkdir('results')

        if(not os.path.exists(pdCsv.addr)):
            dictTemp = {
                '#': [],
                '품목': [],
                '시작 시간': [],
                '마감 시간': [],
                '줄 세운 사람': [],
                '주작 결과': []
            }

            dfTemp = pd.DataFrame(dictTemp)
            dfTemp.to_csv(pdCsv.addr, encoding='utf-8-sig')

            pdCsv.csv = pd.read_csv(pdCsv.addr, encoding='utf-8-sig', index_col = 0)
            return 0

        pdCsv.csv = pd.read_csv(pdCsv.addr, encoding='utf-8-sig', index_col = 0)

        try:
            last = pdCsv.csv.iat[pdCsv.csv.index[-1], 0]
        except:
            return 0
            
        return last

    def save_csv(dict):
        dfTemp = pd.DataFrame(dict)
        pdCsv.csv = pd.concat([pdCsv.csv, dfTemp], ignore_index=True)
        pdCsv.csv.to_csv(pdCsv.addr, encoding='utf-8-sig')
        #print(pdCsv.csv.iat[pdCsv.csv.index[-1], 0])
