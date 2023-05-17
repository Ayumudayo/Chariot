from datetime import datetime
from pytz import timezone
from math import trunc

from Utils.Log import Logger as lg

class Epoch:
    # Convert Datetime to Timestamp

    def ConvertTime(year, month, day, hour, min, sec):

        try:
            srcTime = f'{year}-{month}-{day} {hour}:{min}:{sec} +0900'
            utc = datetime.strptime(srcTime, '%Y-%m-%d %H:%M:%S %z')

            # Drop point
            detStamp = trunc(utc.timestamp())

        except:
            lg.error("Wrong Datetime Input")
            detStamp = 0

        return detStamp

    # Convert Timestamp to formatted string
    def ConvertStamp(stamp):

        try:
            detTime = datetime.fromtimestamp(stamp, timezone('Asia/Seoul'))
            detTime = detTime.strftime('%Y-%m-%d %H:%M:%S')

        except:
            lg.error("Something went wrong while processing ConvertStamp()!!")
            detTime = 0

        return detTime