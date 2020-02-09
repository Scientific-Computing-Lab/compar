import pymongo
import itertools
from bson import json_util
from exceptions import DatabaseError

COMPILATION_PARAMS_FILE_PATH = "assets/compilation_params.json"
COMBINATIONS_DATA_FILE_PATH = "assets/combinations_data.json"
STATIC_DB_NAME = "combinations"
STATIC_COLLECTION_NAME = "combinations"
DYNAMIC_DB_NAME = "results"
DB = "mongodb://10.10.10.120:27017"


class Database:

    def __init__(self, collection_name):
        try:
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
                raise DatabaseError("results DB already has {0} name collection!".format(self.collection_name))
        except Exception as e:
            raise DatabaseError(str(e) + "\nFailed to initialize DB!")

    def initialize_static_db(self):
        try:
            with open(COMBINATIONS_DATA_FILE_PATH, 'r') as f:
                comb_array = json_util.loads(f.read())
                for current_id, comb in enumerate(comb_array, 1):
                    comb["_id"] = str(current_id)
                    self.static_db[STATIC_COLLECTION_NAME].insert_one(comb)
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
            if 'error' not in combination.keys():
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


def generate_combinations():
    try:
        with open(COMPILATION_PARAMS_FILE_PATH, 'r') as f:
            comb_array = json_util.loads(f.read())
            for current_id, comb in enumerate(comb_array, 1):
                print(comb["compiler"])
                compiler = comb["compiler"]
                essential_valued_params_list = generate_valued_params_list(comb["essential_params"]["valued"], True)
                essential_valued_params_list = mult_lists(essential_valued_params_list)
                essential_toggle_params_list = generate_toggle_params_list(comb["essential_params"]["toggle"], True)
                essential_toggle_params_list = mult_lists(essential_toggle_params_list)

                optional_valued_params_list = generate_valued_params_list(comb["optional_params"]["valued"])
                optional_valued_params_list = mult_lists(optional_valued_params_list)
                optional_toggle_params_list = generate_toggle_params_list(comb["optional_params"]["toggle"])
                optional_toggle_params_list = mult_lists(optional_toggle_params_list)

                all_combs = [essential_valued_params_list, essential_toggle_params_list, optional_valued_params_list, optional_toggle_params_list]
                all_combs = [x for x in all_combs if x != [] and x != [""]]
                all_combs = mult_lists(all_combs)

                print(len(all_combs))

                print(all_combs)

                #TODO: add env flags to all combinations, create the combinations and push them to mongoDB

            return True

    except Exception as e:
        print("cannot initialize static DB!")
        print(e)
        return False


def generate_toggle_params_list(toggle, mandatory=False):
    lst = []

    for val in toggle:
        lst.append(generate_toggle_params(val, mandatory))

    return lst


def generate_toggle_params(toggle, mandatory=False):
    if not toggle:
        return [""]

    lst = []

    if not mandatory:
        lst.append("")

    lst.append(toggle)

    return lst


def generate_valued_params(valued, mandatory=False):
    if not valued:
        return [""]

    lst = []

    if not mandatory:
        lst.append("")

    param = valued["param"]
    annotation = valued["annotation"]

    for val in valued["values"]:
        lst.append(param + annotation + str(val))

    return lst


def generate_valued_params_list(valued_list, mandatory=False):
    lst = []

    for valued in valued_list:
        lst.append(generate_valued_params(valued, mandatory))

    return lst


def mult_lists(lst):
    mult_list = []
    for i in itertools.product(*lst):
        i = list(filter(None, list(i))) # remove white spaces
        mult_list.append(" ".join(i))
    return mult_list



generate_combinations()