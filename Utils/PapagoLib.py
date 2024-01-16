import random
import requests
import json
import os

class Translator():    

    def __init__(self):
        with open("./keys.json", 'r') as f:
            cfg = json.load(f)

        f.close()

        self.TR_Cliend_Id = os.getenv('TR_Cliend_Id')
        self.TR_Cliend_Secret = os.getenv('TR_Cliend_Secret')
        self.LD_Cliend_Id = os.getenv('LD_Cliend_Id')
        self.LD_Cliend_Secret = os.getenv('LD_Cliend_Secret')
        self.sdList = [('ko', 'fr'), ('fr', 'en'), ('en', 'zh-CN'), ('zh-CN', "ko")]        

    def request_papago(self, source, target, text):
        papago_url = 'https://openapi.naver.com/v1/papago/n2mt'
        papago_headers = {
            'X-Naver-Client-Id': self.TR_Cliend_Id,
            'X-Naver-Client-Secret': self.TR_Cliend_Secret
        }
        papago_data = {
            'source': source,
            'target': target,
            'text': text
        }
        papago_response = requests.post(papago_url, headers=papago_headers, data=papago_data)
        return papago_response.json()

    def request_papago_lang_dect(self, text):
        papagoLD_url = 'https://openapi.naver.com/v1/papago/detectLangs'
        papagoLD_headers = {
            'X-Naver-Client-Id': self.LD_Cliend_Id,
            'X-Naver-Client-Secret': self.LD_Cliend_Secret
        }
        papagoLD_data = {
            'query': text
        }
        papagoLD_response = requests.post(papagoLD_url, headers=papagoLD_headers, data=papagoLD_data)
        return papagoLD_response.json()

    def translate(self, text):
        langCode = self.lang_dect(text)
        papago_result = self.request_papago(langCode, 'ko', text)
        return papago_result['message']['result']['translatedText']
    
    def lang_dect(self, text):
        papagoLD_result = self.request_papago_lang_dect(text)
        return papagoLD_result['langCode']

    def translateKD(self, text, i = 0):
        count = i
        papago_result = self.request_papago(self.sdList[count][0], self.sdList[count][1], text)

        if(count == 3):
            return papago_result['message']['result']['translatedText']

        return self.translateKD(papago_result['message']['result']['translatedText'], count + 1)

    def lang_dectKD(self, text):
        papagoLD_result = self.request_papago_lang_dect(text)
        return papagoLD_result['langCode'] == 'ko'

    def get_res(self, input, insert = True):
        output = self.translateKD(input, 0)
        outputList = list(output)

        if(insert):
            tmp = 1
            leng = len(outputList)

            while (tmp < leng):
                rndVal = random.randint(1, 4)

                if(outputList[tmp] == ' '):
                    tmp + 1
                else:
                    outputList.insert(tmp, ' ')

                tmp += rndVal
                leng = len(outputList)

            output = ''.join(outputList)

        return output