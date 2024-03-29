import requests
import json
import os

rapidapi_key = os.getenv("RapidAPI_Key")

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