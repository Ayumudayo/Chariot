import requests
import json

with open("./keys.json", 'r') as f:
    cfg = json.load(f)

rapidapi_key = cfg["RapidAPI"]["RapidAPI_Key"]

f.close()

class deepl_translator:

    async def dl_trans(src, dst, query):        

        url = "https://deepl-translator.p.rapidapi.com/translate"

        payload = {
        	"text": query,
        	"source": src,
        	"target": dst
        }
        headers = {
        	"content-type": "application/json",
        	"X-RapidAPI-Key": rapidapi_key,
        	"X-RapidAPI-Host": "deepl-translator.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)

        result = response.json()['text']
        return result