import pymongo;
import collections  # From Python standard library.
import bson
from bson.codec_options import CodecOptions


class database:

    def __init__(self):
        #TODO check if already exists
        self.connection = pymongo.MongoClient('mongodb://localhost:27017')

        self.static_db = self.connection['combinations']
        self.dynamic_db = self.connection['results']

        if('combinations' not in self.static_db.collection_names()):
            self.static_db.create_collection('combinations')
            self.initialize_static_db("file_name", "file_directory") #TODO

        if('results' not in self.dynamic_db.collection_names()):
            self.dynamic_db.create_collection('results')


        self.current_combination_id = 0

    def initialize_static_db(self,file_name,file_directory):
        #TODO insert all combinations from a file with increased integer/ Check if collection named combinations exists
        f = open(r"/Users/reuvenfarag/PycharmProjects/compar_final_project_sce/assets/data.json","r")
        # {"compiler": "autopar",env_params: ['sd','bb',rr'],"code_params": ['nn','jj','oo'],"compiler_params": ['pp','uu'], "combination_id" : 5}
        json = f.read()
        my_data = bson.BSON.encode(json)
        print(my_data)
        self.static_db['combinations'].insert_many(f.read())


        pass

    def get_next_combination(self):

        #return None when there are no more combinations

        self.current_combination = self.static_db.find_one({"_id": self.current_combination_id})
        self.current_combination_id += 1
        return self.current_combination


    def insert_new_combination(self,collection_name,combination_result):
        try:
            self.dynamic_db[collection_name].insert_one(combination_result)
            return True
        except Exception as e:
            print("Combination insertion failed")
            print(e)
            return False

    def delete_combination(self,collection_name,combination_id):
        try:
            self.dynamic_db[collection_name].delete_one({"_id": combination_id})
            return True
        except Exception as e:
            print("Could not delete combination")
            print(e)
            return False

    def find_optimal_loop_combination(self,collection_name,file_name,loop_label):
        # connect = self.dynamic_db[collection_name]
        # combinations = connect.find_one({"combinations_results": { "run_time_results": { "file_name": file_name}}})

        best_speedup = 1
        best_combination_id = -1

        combinations = self.dynamic_db[collection_name].find({})
        for combination in combinations:
            for file in combination['run_time_results']:
                if(file['file_name'] == file_name):
                    for loop in file['loops']:
                        if(loop['loop_label'] == loop_label):
                            if(loop['speedup'] > best_speedup ):
                                best_speedup = loop['speedup']
                                best_combination_id = combination['combination_id']

        return best_combination_id


    def get_combination_from_static_db(self,combination_id):
        try:
            combination = self.static_db.find_one({"_id": combination_id})
        except Exception as e:
            print("Could not find combination")
            print(e)
        finally:
            return combination

x = database()
test = x.find_optimal_loop_combination('Autopar','bin.c','l1')
x.initialize_static_db("adsa","dasas")
print(test)
# x.create_new_collection('Autopar')
# x.insert_new_combination('Autopar',{'test': 'test'})