import os
import json
import threading
import pytz
import re
import requests

from datetime import datetime
from xml.etree import ElementTree as ET

from Utils.PapagoLib import Translator
from Utils.Log import Logger

class Parser:
    
    RSS_URL = 'https://jp.finalfantasyxiv.com/lodestone/news/news.xml'
    JST_TIMEZONE = pytz.timezone('Asia/Tokyo')
    FILE_PATH = './Data/Maint/maintinfo.json'
    DIR_PATH = './Data/Maint'

    def __init__(self):
        self.now_jst = self.JST_TIMEZONE.localize(datetime.now())

    # File operations
    def save_maint_info(self,s_stamp, e_stamp, title, title_kr, url):
        maint_data = {
            "start_stamp": s_stamp,
            "end_stamp": e_stamp,
            "title": title,
            "title_kr": title_kr,
            "url": url
        }

        with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(maint_data, f, indent=4, ensure_ascii=False)

    def load_maint_info(self):
        # 폴더의 존재 여부를 확인
        if not os.path.exists(os.path.dirname(self.DIR_PATH)):
            # 폴더가 없으면 생성
            os.makedirs(os.path.dirname(self.DIR_PATH), exist_ok=True)
            return None

        # 폴더가 존재하면 파일 열기 시도
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 파일이 없는 경우 None 반환
            return None

    # RSS Parsing
    def parse_rss_feed(self):
        response = requests.get(self.RSS_URL)
        if response.status_code != 200:
            return None
        # {http://www.w3.org/2005/Atom}
        root = ET.fromstring(response.content)

        # I don't know why, it doesn't work w/o {http://www.w3.org/2005/Atom}, 
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            if '全ワールド' in title:
                link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                content = entry.find('{http://www.w3.org/2005/Atom}content').text
                time_string = self.extract_time_info(content)
                if time_string:
                    tr = Translator()
                    title_kr = tr.translate(title)                    
                    start_unix_timestamp, end_unix_timestamp = self.parse_time_string(time_string)
                    return start_unix_timestamp, end_unix_timestamp, title, title_kr, link
        return None

    @staticmethod
    def extract_time_info(content):
        time_match = re.search(r"日\s*時：(.*?)終了", content, re.DOTALL)
        return time_match.group(1) if time_match else None

    def parse_time_string(self, time_string):
        time_string = re.sub(r'<br\s*/?>', '', time_string)  # Remove HTML line breaks
        time_string = re.sub(r'[\r\n]', '', time_string)  # Remove new lines

        start_match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]+\)\s*(\d{1,2}):(\d{1,2})より", time_string)
        end_match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]+\)\s*(\d{1,2}):(\d{1,2})頃まで", time_string)

        if start_match and end_match:
            s_year, s_month, s_day, start_hour, start_minute = map(int, start_match.groups())
            e_year, e_month, e_day, end_hour, end_minute = map(int, end_match.groups())

            start_datetime = self.JST_TIMEZONE.localize(datetime(s_year, s_month, s_day, start_hour, start_minute))
            end_datetime = self.JST_TIMEZONE.localize(datetime(e_year, e_month, e_day, end_hour, end_minute))

            return int(start_datetime.timestamp()), int(end_datetime.timestamp())
        else:
            # Handle case where either start or end time information is not found
            return None, None


    def get_maintenance_timestamp(self):
        try:
            json_data = self.load_maint_info()
        except FileNotFoundError:
            json_data = None

        if json_data and json_data["end_stamp"] >= self.now_jst.timestamp():
            return json_data["start_stamp"], json_data["end_stamp"], json_data["title"], json_data["title_kr"],  json_data["url"]

        parsed_data = self.parse_rss_feed()
        if parsed_data:
            print(parsed_data)
            start_unix_timestamp, end_unix_timestamp, title, title_kr, url = parsed_data
            if end_unix_timestamp >= self.now_jst.timestamp():
                return start_unix_timestamp, end_unix_timestamp, title, title_kr, url
        
            self.save_maint_info(start_unix_timestamp, end_unix_timestamp, title, title_kr, url)
            
        return None
    
    def check_for_maintenance(self):
        Logger.info("Checking for maintenance...")

        maint_info = self.get_maintenance_timestamp()
        if maint_info:
            Logger.info("Maintenance information updated.")
        else:
            Logger.info("Failed to retrieve maintenance information. May be a maintenance in progress.")

        # Schedule the next check after 24 hours
        threading.Timer(24 * 3600, self.check_for_maintenance).start()