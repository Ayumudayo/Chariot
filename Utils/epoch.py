from datetime import datetime
from pytz import timezone
from math import trunc

from Utils.Log import Logger as lg

class Epoch:
    # Convert Datetime to Timestamp

    def ConvertTime(year, month, day, hour, min, sec):
        try:
            # �Էµ� ��¥�� �ð��� datetime ��ü�� �����ϰ� Ÿ������ ���� ����
            input_time = timezone('Asia/Tokyo').localize(datetime(year, month, day, hour, min, sec))

            # JST �ð��� Ÿ�ӽ������� ��ȯ
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