import pymongo;

class database:

    def __init__(self):
        #TODO check if already exists
        self.connection = pymongo.MongoClient('mongodb://localhost:27017')
        # self.static_db = self.connection['combinations']
        self.dynamic_db = self.connection['results']

        # self.static_db.create_collection('combinations')
        self.initialize_static_db("hello","bye")
        self.current_combination_id = 0

    def initialize_static_db(self,file_name,file_directory):
        #TODO insert all combinations from a file with increased integer/ Check if collection named combinations exists
        pass

    def get_next_combination(self):

        #return None when there are no more combinations

        self.current_combination = self.static_db.find_one({"_id": self.current_combination_id})
        self.current_combination_id += 1
        return self.current_combination

    def create_new_collection(self,name):
        try:
            self.dynamic_db.create_collection(name)
            return True
        except Exception as e:
            print("Collection named ${0} already exists".format(name))
            print(e)
            return False

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

    def find_optimal_loop_combination(self,collection_name,file_name,loop_id):
        # connect = self.dynamic_db[collection_name]
        # combinations = connect.find_one({"combinations_results": { "run_time_results": { "file_name": file_name}}})
        combinations = self.dynamic_db[collection_name].find_one({"combinations_results": {"combination_id": 15}})
        print(combinations)


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
print(test)
# x.create_new_collection('Autopar')
# x.insert_new_combination('Autopar',{'test': 'test'})