from concurrent.futures import ThreadPoolExecutor
import requests
import os
from Utils.Log import Logger as lg

class Exchange():

    @staticmethod
    def fetch_rate(src, dst, amount):
        try:
            request = requests.get(f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{src}/{dst}.min.json")
            result = request.json()
            total = result[f'{dst}'] * amount
            return '{:,.2f}'.format(total), None
        except Exception as e:
            lg.error("Something went wrong while processing fetch_rate()!!")
            return 0, e

    # 화폐 코드 입력하여 API가 지원하는 모든 화폐단위에 대한 환율 제공
    def exchCur(self, src, amount, dst):
        total, err = self.fetch_rate(src, dst, amount)
        if err:
            total = 0
        return total

    def fetch_exchange_rate(self, src, dst, amount):
        return dst, self.fetch_rate(src, dst, amount)[0]

    def exchCurList(self, src, amount):
        dst_currencies = ['usd', 'krw', 'jpy', 'eur', 'gbp', 'cny', 'try', 'ars', 'twd', 'mnt']
        exchange_rates = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.fetch_exchange_rate, src, dst, amount) for dst in dst_currencies]

            for future in futures:
                try:
                    dst, total = future.result()
                    if total is not None:
                        exchange_rates[dst] = total
                except Exception as e:
                    lg.error(f"An exception occurred: {e}")

        return exchange_rates
