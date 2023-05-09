from datetime import datetime, timedelta, timezone
from pytz import timezone
from enum import Enum

class types(Enum):
    INFO = 1
    ERROR = 2
    DEBUG = 3
    UNKNOWN = 4

class Colors:
    BLACK = '[\033[30m'
    RED = '[\033[31m'
    GREEN = '[\033[32m'
    YELLOW = '[\033[33m'
    BLUE = '[\033[34m'
    MAGENTA = '[\033[35m'
    CYAN = '[\033[36m'
    WHITE = '[\033[37m'
    UNDERLINE = '[\033[4m'
    RESET = '\033[0m]'

class Logger:

    def __init__(self):
        super().__init__()
        Logger.KST = timezone('Asia/Seoul')

    #Logging function
    @staticmethod
    def pushLog(lTypes, content, datetime):

        from Database.dynamo import awsDynamo as ad
        handle = ad()

        data = {
         "LOG": "LOG",
         "logNumber": handle.getLogNumber() + 1,
         "content": content,
         "dateTime": f'{datetime}',
         "logType": lTypes
        }

        handle.push(data, 'log')


    @staticmethod
    def info(content):

        today = datetime.now().astimezone(Logger.KST)
        lt = Colors.BLUE + types.INFO.name + Colors.RESET

        Logger.pushLog(types.INFO.name, content, today)

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<18} {str}'.format(type = lt, str = content))
    
    @staticmethod
    def error(content):

        today = datetime.now().astimezone(Logger.KST)
        lt = Colors.RED + types.ERROR.name + Colors.RESET

        Logger.pushLog(types.ERROR.name, content, today)

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<18} {str}'.format(type = lt, str = content))
    
    @staticmethod
    def debug(content):

        today = datetime.now().astimezone(Logger.KST)
        lt = Colors.GREEN + types.DEBUG.name + Colors.RESET

        Logger.pushLog(types.DEBUG.name, content, today)

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<18} {str}'.format(type = lt, str = content))
    
    @staticmethod
    def unknown(content):

        today = datetime.now().astimezone(Logger.KST)
        lt = Colors.YELLOW + types.UNKNOWN.name + Colors.RESET

        Logger.pushLog(types.UNKNOWN.name, content, today)

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<18} {str}'.format(type = lt, str = content))