from .nasdaqRtb import RedBlackTree
from .Log import Logger

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class RbtInit:
    def __init__(self, csvPath="./Data/Stock/nasdaq_screener.csv", jsonPath="./Data/Stock/rbt.json"):
        self.rbt = RedBlackTree()
        self.csvPath = csvPath
        self.jsonPath = jsonPath

    # Function to create Red-Black Tree from CSV file and save it to a JSON file
    def create_rbt_from_csv_and_save(self):
        self.rbt.insert_from_csv(self.csvPath)
        self.rbt.save_to_json(self.jsonPath)

    def check_file_exist(self):
        try:
            with open(self.jsonPath, "r") as json_file:
                #Logger.debug("rbt.json exist")
                return True
        except FileNotFoundError:
            #Logger.debug("rbt.json not exist")
            return False
        
    def init_rbt(self):
        if self.check_file_exist():
            self.rbt.load_from_json(self.jsonPath)
        else:
            self.create_rbt_from_csv_and_save()

        return self.rbt

class SeleBrowserInit:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
        self.chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-logging')
        self.chrome_options.add_argument('--disable-cookies')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def init_browser(self):
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)