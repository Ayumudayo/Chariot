import json
import pytz
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


class Parser:
    
    TARGET_URL = 'https://jp.finalfantasyxiv.com/lodestone/news/category/2'
    JST_TIMEZONE = pytz.timezone('Asia/Tokyo')

    def __init__(self):
        self.now_jst = self.JST_TIMEZONE.localize(datetime.now())

    # File operations
    @staticmethod
    def save_maint_info(s_stamp, e_stamp, title, url):
        maint_data = {
            "start_stamp": s_stamp,
            "end_stamp": e_stamp,
            "title": title,
            "url": url
        }

        with open("./maintinfo.json", 'w', encoding='utf-8') as f:
            json.dump(maint_data, f, indent=4, ensure_ascii=False)
           
    @staticmethod
    def load_maint_info():
        try:
            with open("./maintinfo.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    # Web scraping
    def get_recent_maintenance_title(self):
        response = requests.get(self.TARGET_URL)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        target_prefix = "全ワールド"
        news_list_elements = soup.find_all(class_="news__list")
        current_year = self.now_jst.year
        
        for news_element in news_list_elements:
            title_elements = news_element.find_all(class_="news__list--title")
            for title_element in title_elements:
                title_text = "".join(str(item) for item in title_element.contents if item.name is None).strip()
        
                if title_text.startswith(target_prefix):
                    date_text = title_text.split('(')[-1].replace(')', '')
                    month, day = map(int, re.split('[/-]', date_text)[:2])

                    post_datetime = self.JST_TIMEZONE.localize(datetime(current_year, month, day))
        
                    if (self.now_jst - post_datetime).days < 1:
                        return title_text, news_element.find('a')['href']
        
        return None, None

    # Parsing
    def get_html_content(self, url):
        response = requests.get(url)
        return response.content if response.status_code == 200 else None

    @staticmethod
    def parse_html_content(html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        news_detail_div = soup.find("div", class_="news__detail__wrapper")
        return news_detail_div.get_text()

    @staticmethod
    def extract_time_info(content):
        time_match = re.search(r"日\s*時：(.*?)※", content, re.DOTALL)
        return time_match.group(1) if time_match else None

    def parse_time_string(self, time_string):
        matches = list(re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日").finditer(time_string))
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

        title, link = self.get_recent_maintenance_title()
        if not link:
            return None

        url = f'https://jp.finalfantasyxiv.com{link}'
        html_content = self.get_html_content(url)
        if not html_content:
            return None

        content = self.parse_html_content(html_content)
        time_string = self.extract_time_info(content)

        if time_string:
            start_unix_timestamp, end_unix_timestamp = self.parse_time_string(time_string)
            if end_unix_timestamp >= self.now_jst.timestamp():
                self.save_maint_info(start_unix_timestamp, end_unix_timestamp, title, url)
                return start_unix_timestamp, end_unix_timestamp, title, url
        
        return None
