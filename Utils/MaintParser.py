import json
import pytz
import re
import requests

from datetime import datetime
from xml.etree import ElementTree as ET

class Parser:
    
    RSS_URL = 'https://jp.finalfantasyxiv.com/lodestone/news/news.xml'
    JST_TIMEZONE = pytz.timezone('Asia/Tokyo')

    def __init__(self):
        self.now_jst = self.JST_TIMEZONE.localize(datetime.now())

    # File operations
    def save_maint_info(s_stamp, e_stamp, title, url):
        maint_data = {
            "start_stamp": s_stamp,
            "end_stamp": e_stamp,
            "title": title,
            "url": url
        }

        with open("./maintinfo.json", 'w', encoding='utf-8') as f:
            json.dump(maint_data, f, indent=4, ensure_ascii=False)

    def load_maint_info():
        try:
            with open("./maintinfo.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    # RSS Parsing
    def parse_rss_feed(self):
        response = requests.get(self.RSS_URL)
        if response.status_code != 200:
            return None
        # {http://www.w3.org/2005/Atom}
        root = ET.fromstring(response.content)
        for entry in root.findall('entry'):
            title = entry.find('title').text
            if '全ワールド' in title:
                link = entry.find('link').attrib['href']
                content = entry.find('content').text
                time_string = self.extract_time_info(content)
                if time_string:
                    start_unix_timestamp, end_unix_timestamp = self.parse_time_string(time_string)
                    return start_unix_timestamp, end_unix_timestamp, title, link
        return None

    @staticmethod
    def extract_time_info(content):
        time_match = re.search(r"日\s*時：(.*?)<br>", content, re.DOTALL)
        return time_match.group(1) if time_match else None

    def parse_time_string(self, time_string):
        time_string = re.sub(r'<br\s*/?>', '', time_string)  # Remove HTML line breaks
        time_string = re.sub(r'[\r\n]', '', time_string)  # Remove new lines

        matches = list(re.finditer(r"(\d{4})年(\d{1,2})月(\d{1,2})日", time_string))
        s_year, s_month, s_day = map(int, matches[0].groups())
        e_year, e_month, e_day = map(int, matches[1].groups()) if len(matches) > 1 else (s_year, s_month, s_day)

        start_hour, start_minute = map(int, re.search(r"(\d{1,2}):(\d{1,2})より", time_string).groups())
        end_hour, end_minute = map(int, re.search(r"(\d{1,2}):(\d{1,2})頃まで", time_string).groups())

        start_datetime = self.JST_TIMEZONE.localize(datetime(s_year, s_month, s_day, start_hour, start_minute))
        end_datetime = self.JST_TIMEZONE.localize(datetime(e_year, e_month, e_day, end_hour, end_minute))

        return int(start_datetime.timestamp()), int(end_datetime.timestamp())

    def get_maintenance_timestamp(self):
        json_data = self.load_maint_info()
        if json_data and json_data["end_stamp"] >= self.now_jst.timestamp():
            return json_data["start_stamp"], json_data["end_stamp"], json_data["title"], json_data["url"]

        parsed_data = self.parse_rss_feed()
        if parsed_data:
            start_unix_timestamp, end_unix_timestamp, title, url = parsed_data
            if end_unix_timestamp >= self.now_jst.timestamp():
                self.save_maint_info(start_unix_timestamp, end_unix_timestamp, title, url)
                return start_unix_timestamp, end_unix_timestamp, title, url
        
        return None