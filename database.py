import pymongo
from bson import json_util


COMBINATIONS_DATA_FILE_PATH = "assets/combinations_data.json"
STATIC_DB_NAME = "combinations"
STATIC_COLLECTION_NAME = "combinations"
DYNAMIC_DB_NAME = "results"
DB = "mongodb://localhost:27017"


class Database:

    def __init__(self, collection_name):
        self.current_combination = None
        self.current_combination_id = 1
        self.collection_name = collection_name
        self.connection = pymongo.MongoClient(DB)
        self.static_db = self.connection[STATIC_DB_NAME]
        self.dynamic_db = self.connection[DYNAMIC_DB_NAME]

        if STATIC_COLLECTION_NAME not in self.static_db.list_collection_names():
            self.static_db.create_collection(STATIC_COLLECTION_NAME)
            self.initialize_static_db()

        if self.collection_name not in self.dynamic_db.list_collection_names():
            self.dynamic_db.create_collection(self.collection_name)
        else:
            raise Exception("results DB already has {0} name collection!".format(self.collection_name))

    def initialize_static_db(self):
        try:
            f = open(COMBINATIONS_DATA_FILE_PATH, "r")
            comb_array = json_util.loads(f.read())
            current_id = 0
            for comb in comb_array:
                comb["_id"] = str(current_id)
                self.static_db[STATIC_COLLECTION_NAME].insert_one(comb)
                current_id += 1
            return True

        except Exception as e:
            print("cannot initialize static DB!")
            print(e)
            return False

    def get_next_combination(self):
        self.current_combination = self.static_db[STATIC_COLLECTION_NAME].find_one({"_id": str(self.current_combination_id)})
        self.current_combination_id += 1
        return self.current_combination

    def has_next_combination(self):
        checked_combination = self.static_db[STATIC_COLLECTION_NAME].find_one({"_id": str(self.current_combination_id)})
        return checked_combination is not None

    def insert_new_combination(self, combination_result):
        try:
            self.dynamic_db[self.collection_name].insert_one(combination_result)
            return True
        except Exception as e:
            print("Combination insertion failed")
            print(e)
            return False

    def delete_combination(self, combination_id):
        try:
            self.dynamic_db[self.collection_name].delete_one({"_id": combination_id})
            return True
        except Exception as e:
            print("Could not delete combination")
            print(e)
            return False

    def find_optimal_loop_combination(self, file_name, loop_label):
        best_speedup = 1
        best_combination_id = 0
        combinations = self.dynamic_db[self.collection_name].find({})
        for combination in combinations:
            for file in combination['run_time_results']:
                if file['file_name'] == file_name:
                    for loop in file['loops']:
                        if loop['loop_label'] == loop_label:
                            if loop['speedup'] > best_speedup:
                                best_speedup = loop['speedup']
                                best_combination_id = combination['_id']

        return best_combination_id

    def get_combination_from_static_db(self, combination_id):
        combination = None
        try:
            combination = self.static_db[STATIC_COLLECTION_NAME].find_one({"_id": combination_id})
        except Exception as e:
            print("Could not find combination")
            print(e)
        finally:
            return combination
