import pytz

from datetime import datetime

# 공휴일 리스트
holidays = [
    "2023-01-02",  # New Year's Day
    "2023-01-16",  # Martin Luther King Jr. Day
    "2023-02-20",  # Presidents' Day
    "2023-04-07",  # Good Friday
    "2023-05-29",  # Memorial Day
    "2023-07-04",  # Independence Day
    "2023-09-04",  # Labor Day
    "2023-11-23",  # Thanksgiving Day
    "2023-12-25"   # Christmas Day
]

class NasdaqOpenChecker:
    @staticmethod
    def is_nasdaq_open():
        # 현재 시간을 미 동부 표준시로 변환
        current_time = datetime.now(pytz.timezone('US/Eastern'))

        # NASDAQ 개장 시간 (9:30 AM - 4:00 PM, 월-금)
        open_time = current_time.replace(hour=9, minute=30, second=0)
        close_time = current_time.replace(hour=16, minute=0, second=0)

        # 현재 요일 확인 (월요일은 0, 일요일은 6)
        current_day_of_week = current_time.weekday()

        # 현재 날짜가 공휴일인지 확인
        is_holiday = current_time.strftime('%Y-%m-%d') in holidays

        # 현재 시간이 개장 시간 내이고, 현재 요일이 월-금인지, 그리고 공휴일이 아닌지 확인
        return open_time <= current_time <= close_time and 0 <= current_day_of_week <= 4 and not is_holiday
