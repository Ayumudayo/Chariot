from datetime import datetime
from pytz import timezone
from math import trunc

from Utils.Log import Logger as lg

class Epoch:
    # Convert Datetime to Timestamp

    def ConvertTime(year, month, day, hour, min, sec):
        try:
            # 입력된 날짜와 시간을 datetime 객체로 생성하고 타임존을 직접 설정
            input_time = timezone('Asia/Tokyo').localize(datetime(year, month, day, hour, min, sec))

            # JST 시간을 타임스탬프로 변환
            timestamp = trunc(int(input_time.timestamp()))

        except Exception as e:
            lg.error(f"Something went wrong while processing ConvertTime()!!\nError: {e}")
            timestamp = 0
        return timestamp

    # Convert Timestamp to formatted string
    def ConvertStamp(stamp):

        try:
            detTime = datetime.fromtimestamp(stamp, timezone('Asia/Tokyo'))
            detTime = detTime.strftime('%Y-%m-%d %H:%M:%S')

        except Exception as e:
            lg.error(f"Something went wrong while processing ConvertStamp()!!\nError: {e}")
            detTime = 0

        return detTime