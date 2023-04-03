import requests

class Exchange():

    # 화폐 코드 입력하여 API가 지원하는 모든 화폐단위에 대한 환율 제공
    def exchCur(src, amount, dst):
        request = requests.get(f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{src}/{dst}.min.json")

        result = request.json()
        total = result[f'{dst}'] * amount

        total = round(total, 2)
        total = format(total, ',')

        return total