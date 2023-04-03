import os
import random
import sys
import urllib.request
import requests

class Translator():    

    def __init__(self, T_Id, T_Sec, L_Id, L_Sec):
        super().__init__()
        Translator.value = None
        Translator.TR_Cliend_Id = T_Id
        Translator.TR_Cliend_Secret = T_Sec
        Translator.LD_Cliend_Id = L_Id
        Translator.LD_Cliend_Secret = L_Sec
        Translator.sdList = []

        Translator.sdList.append(('ko', 'fr'))
        Translator.sdList.append(('fr', 'en'))
        Translator.sdList.append(('en', 'zh-CN'))
        Translator.sdList.append(('zh-CN', "ko"))

    def Translate(text, i = 0):
        
        count = i

        papago_url = 'https://openapi.naver.com/v1/papago/n2mt'
        papago_headers = {
            'X-Naver-Client-Id': Translator.TR_Cliend_Id,
            'X-Naver-Client-Secret': Translator.TR_Cliend_Secret
        }
        papago_data = {
            'source': Translator.sdList[count][0],
            'target': Translator.sdList[count][1],
            'text': text
        }
        papago_response = requests.post(papago_url, headers=papago_headers, data=papago_data)
        papago_result = papago_response.json()

        if(count == 3):
            return papago_result['message']['result']['translatedText']

        return Translator.Translate(papago_result['message']['result']['translatedText'], count + 1)

    def LangDect(text):
        papagoLD_url = 'https://openapi.naver.com/v1/papago/detectLangs'
        papagoLD_headers = {
            'X-Naver-Client-Id': Translator.LD_Cliend_Id,
            'X-Naver-Client-Secret': Translator.LD_Cliend_Secret
        }
        papagoLD_data = {
            'query': text
        }
        papagoLD_response = requests.post(papagoLD_url, headers=papagoLD_headers, data=papagoLD_data)
        papagoLD_result = papagoLD_response.json()

        if(papagoLD_result['langCode'] != 'ko'):
            return False
        return True

    def getRes(input, insert = True):

        output = Translator.Translate(input, 0)
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

