import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

class Parser:

    def get_recent_maintenance_title(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser') if response.status_code == 200 else None

        if not soup:
            return None

        target_prefix = "全ワールド"
        news_list_elements = soup.find_all(class_="news__list")
        current_year = datetime.now().year

        for news_element in news_list_elements:
            title_element = news_element.find(class_="news__list--title")
            title_text = "".join(str(item) for item in title_element.contents if item.name is None).strip()

            if title_text.startswith(target_prefix):
                date_text = title_text.split('(')[-1].replace(')', '')
                month, day = map(int, date_text.split('/')[0:2])
                post_datetime = datetime(current_year, month, day)

                if (datetime.now() - post_datetime).days < 1:
                    return title_text, news_element.find('a')['href']

        return None
    
    def get_maint_info():
        target_url = 'https://jp.finalfantasyxiv.com/lodestone/news/category/2'
        recent_title, recent_link = Parser.get_recent_maintenance_title(target_url) or (None, None)

        return recent_title, recent_link

    
    def get_html_content(url):
        response = requests.get(url)
        return response.content

    def parse_html_content(html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        news_detail_div = soup.find("div", class_="news__detail__wrapper")
        return news_detail_div.get_text()

    def extract_time_info(content):
        time_match = re.search(r"日\s*時：(.*?)頃まで", content, re.DOTALL)
        if time_match:
            return time_match.group(1).strip()
        else:
            return None

    def parse_time_string(time_string):
        match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", time_string)
        year, month, day = map(int, match.groups())

        match = re.search(r"(\d{1,2}):(\d{1,2})より(\d{1,2}):(\d{1,2})", time_string)
        start_hour, start_minute, end_hour, end_minute = map(int, match.groups())

        start_datetime = datetime(year, month, day, start_hour, start_minute)
        end_datetime = datetime(year, month, day, end_hour, end_minute)

        return int(start_datetime.timestamp()), int(end_datetime.timestamp())

    def GetMaintTimeStamp():

        # infos[0] = title, infos[1] = link
        infos = Parser.get_maint_info()

        if not infos[1]:
            return None

        url = f'https://jp.finalfantasyxiv.com{infos[1]}'
        html_content = Parser.get_html_content(url)
        content = Parser.parse_html_content(html_content)
        time_string = Parser.extract_time_info(content)

        if time_string:
            start_unix_timestamp, end_unix_timestamp = Parser.parse_time_string(time_string)
            if end_unix_timestamp < datetime.now().timestamp():
                return None
            print(f"Parsed time: {start_unix_timestamp} to {end_unix_timestamp}")
            return start_unix_timestamp, end_unix_timestamp, infos[0], url
        else:
            return None