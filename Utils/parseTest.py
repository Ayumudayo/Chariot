import requests
import logging as lg

def exchCur(src='eur', amount=51650):
    dst_currencies = ['usd', 'krw', 'jpy', 'cny', 'try', 'ars', 'twd']
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
            exchange_rates[dst] = 0

    tlist = list()

    for vals in exchange_rates.values():        
        tlist.append(vals)
        #print(vals)
    
    print(tlist[0])

    return exchange_rates

print(exchCur())