import requests
from Utils.Log import Logger as lg

class Exchange():

    # 화폐 코드 입력하여 API가 지원하는 모든 화폐단위에 대한 환율 제공
    def exchCur(src, amount, dst):

        try:
            request = requests.get(f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{src}/{dst}.min.json")

            result = request.json()
            total = result[f'{dst}'] * amount

            total = '{:,.2f}'.format(total)

        except:
            lg.error("Something went wrong while processing exchCur()!!")
            total = 0

        return total
    

    def exchCurList(src, amount):
        dst_currencies = ['usd', 'krw', 'jpy', 'eur', 'gbp', 'cny', 'try', 'ars', 'twd', 'mnt']
        exchange_rates = {}

        for dst in dst_currencies:
            try:
                request = requests.get(f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{src}/{dst}.min.json")
                result = request.json()
                total = result[f'{dst}'] * amount
                total = '{:,.2f}'.format(total)
                exchange_rates[dst] = total

            except:
                lg.error("Something went wrong while processing exchCur()!!")
                return None
        
        return exchange_rates