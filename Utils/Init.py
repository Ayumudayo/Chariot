from .nasdaqRtb import RedBlackTree

class RbtInit:
    def __init__(self, flag):
        self.rbt = RedBlackTree()
        if flag == 'eqt':
            self.csvPath = "./Data/Stock/nasdaq_screener.csv"
            self.jsonPath = "./Data/Stock/eqt_rbt.json"
        elif flag == 'etf':
            self.csvPath = "./Data/Stock/nasdaq_etf_screener.csv"
            self.jsonPath = "./Data/Stock/etf_rbt.json"



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