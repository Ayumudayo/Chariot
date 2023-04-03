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

    #Loggin function
    def writeLog(lTypes, content):

        # Set Korean Timezone
        KST = timezone('Asia/Seoul')

        today = datetime.now()
        today = today.astimezone(KST)

        lt = None

        # Coloring strings
        if(lTypes == types.INFO.value):
            lt = Colors.BLUE + types.INFO.name + Colors.RESET
        elif(lTypes == types.ERROR.value):
            lt = Colors.RED + types.ERROR.name + Colors.RESET
        elif(lTypes == types.DEBUG.value):
            lt = Colors.GREEN + types.DEBUG.name + Colors.RESET
        elif(lTypes == types.UNKNOWN.value):
            lt = Colors.YELLOW + types.UNKNOWN.name + Colors.RESET

        # Print log on terminal
        print(f'[{today}]', end="    ")
        print('{type:<19} {str}'.format(type = lt, str = content))