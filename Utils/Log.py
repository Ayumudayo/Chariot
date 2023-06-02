from datetime import datetime
from pytz import timezone
from enum import Enum

class LogType(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    UNKNOWN = 'UNKNOWN'

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
    KST = timezone('Asia/Seoul')

    @staticmethod
    def push_log(log_type, content, datetime):
        from Database.dynamo import awsDynamo as ad
        handle = ad()

        data = {
            "LOG": "LOG",
            "logNumber": handle.getLogNumber() + 1,
            "content": content,
            "dateTime": f'{datetime}',
            "logType": log_type.value
        }

        handle.push(data, 'log')

    @staticmethod
    def log(log_type, content):
        today = datetime.now(Logger.KST)
        color = {
            LogType.INFO: Colors.BLUE,
            LogType.ERROR: Colors.RED,
            LogType.DEBUG: Colors.GREEN,
            LogType.UNKNOWN: Colors.YELLOW
        }.get(log_type, Colors.RESET)

        Logger.push_log(log_type, content, today)

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<18} {str}'.format(type=color + log_type.value + Colors.RESET, str=content))

    @staticmethod
    def info(content):
        Logger.log(LogType.INFO, content)

    @staticmethod
    def error(content):
        Logger.log(LogType.ERROR, content)

    @staticmethod
    def debug(content):
        Logger.log(LogType.DEBUG, content)

    @staticmethod
    def unknown(content):
        Logger.log(LogType.UNKNOWN, content)