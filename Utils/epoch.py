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
            #print(utc.tzinfo)
            detStamp = utc.timestamp()

            # Drop point
            #lg.debug(f'Before Trunc {detStamp}')
            detStamp = trunc(detStamp)
            #lg.debug(f'After Trunc {detStamp}')

        except:
            lg.error("Wrong Datetime Input")
            detStamp = 0

        return detStamp

    # Convert Timestamp to formatted string
    def ConvertStamp(stamp):

        try:
            detTime = datetime.fromtimestamp(stamp, timezone('Asia/Seoul'))       
            #lg.debug(f'Time : {detTime}')

            detTime = detTime.strftime('%Y-%m-%d %H:%M:%S')
            #lg.debug(f'Datetime : {detTime}')

        except:
            lg.error("Something went wrong while processing ConvertStamp()!!")
            detTime = 0

        return detTime