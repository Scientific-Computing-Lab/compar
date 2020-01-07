import pymongo
from bson import json_util


class Database:

    def __init__(self):
        self.current_combination = None
        self.current_combination_id = 0
        self.connection = pymongo.MongoClient('mongodb://localhost:27017')
        self.static_db = self.connection['combinations']
        self.dynamic_db = self.connection['results']

        if 'combinations' not in self.static_db.list_collection_names():
            self.static_db.create_collection('combinations')
            self.initialize_static_db("file_name", "file_directory")

        if 'results' not in self.dynamic_db.list_collection_names():
            self.dynamic_db.create_collection('results')

    def initialize_static_db(self, file_path):
        try:
            f = open(file_path, "r")
            comb_array = json_util.loads(f.read())
            for comb in comb_array:
                self.static_db['combinations'].insert_one(comb)
            return True

        except Exception as e:
            print("cannot initialize static DB!")
            print(e)
            return False

    def get_next_combination(self):
        self.current_combination = self.static_db["combinations"].find_one({"_id": self.current_combination_id})
        self.current_combination_id += 1
        return self.current_combination

    def insert_new_combination(self, collection_name, combination_result):
        try:
            self.dynamic_db[collection_name].insert_one(combination_result)
            return True
        except Exception as e:
            print("Combination insertion failed")
            print(e)
            return False

    def delete_combination(self, collection_name, combination_id):
        try:
            self.dynamic_db[collection_name].delete_one({"_id": combination_id})
            return True
        except Exception as e:
            print("Could not delete combination")
            print(e)
            return False

    def find_optimal_loop_combination(self, collection_name, file_name, loop_label):
        best_speedup = 1
        best_combination_id = -1
        combinations = self.dynamic_db[collection_name].find({})
        for combination in combinations:
            for file in combination['run_time_results']:
                if file['file_name'] == file_name :
                    for loop in file['loops']:
                        if loop['loop_label'] == loop_label :
                            if loop['speedup'] > best_speedup:
                                best_speedup = loop['speedup']
                                best_combination_id = combination['combination_id']

        return best_combination_id

    def get_combination_from_static_db(self, combination_id):
        combination = None
        try:
            combination = self.static_db["combinations"].find_one({"_id": combination_id})
        except Exception as e:
            print("Could not find combination")
            print(e)
        finally:
            return combination


# ~~~~~~~~~ Examples
x = Database()
# test = x.find_optimal_loop_combination('Autopar', 'bin.c', 'l1')
# print(test)

#x.initialize_static_db(r"C:\Users\Gilad\Desktop\data.json")

print(x.get_next_combination())
print(x.get_next_combination())
# x.create_new_collection('Autopar')
# x.insert_new_combination('Autopar',{'test': 'test'})

#file example:
'''
[
{
	"compiler": "cetus",
	"env_params": [
		"sd",
		"bb",
		"rr"
	],
	"code_params": [
		"nn",
		"jj",
		"oo"
	],
	"compiler_params": [
		"pp",
		"uu"
	],
	"_id": 2
},
{
	"compiler": "autopar",
	"env_params": [
		"sd",
		"bb",
		"rr"
	],
	"code_params": [
		"nn",
		"jj",
		"oo"
	],
	"compiler_params": [
		"pp",
		"uu"
	],
	"_id": 1
}
]'''