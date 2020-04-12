import pymongo
import itertools
from bson import json_util
from exceptions import DatabaseError, MissingDataError, DeadCodeLoop, DeadCodeFile, NoOptimalCombinationError
from job import Job
import logger
import traceback
import hashlib

COMPILATION_PARAMS_FILE_PATH = "assets/compilation_params.json"
ENVIRONMENT_PARAMS_FILE_PATH = "assets/env_params.json"
STATIC_DB_NAME = "compar_combinations"
DYNAMIC_DB_NAME = "compar_results"
DB = "mongodb://10.10.10.120:27017"


class Database:

    SERIAL_COMBINATION_ID = 'serial'
    SERIAL_COMPILER_NAME = 'serial'

    def __init__(self, collection_name):
        logger.info(f'Initializing {collection_name} databases')
        try:
            self.dynamic_combinations_cursor = None
            self.collection_name = collection_name
            self.connection = pymongo.MongoClient(DB)
            self.static_db = self.connection[STATIC_DB_NAME]
            self.dynamic_db = self.connection[DYNAMIC_DB_NAME]

            if self.collection_name in self.static_db.list_collection_names():
                # TODO: should be depend on users choice
                self.static_db.drop_collection(self.collection_name)

            self.static_db.create_collection(self.collection_name)
            self.initialize_static_db()

            if self.collection_name in self.dynamic_db.list_collection_names():
                self.dynamic_db.drop_collection(self.collection_name)

            self.dynamic_db.create_collection(self.collection_name)

        except Exception as e:
            raise DatabaseError(str(e) + "\nFailed to initialize DB!")

    def initialize_static_db(self):
        try:
            combinations = generate_combinations()
            for combination in combinations:
                curr_combination_id = Database.generate_combination_id(combination)
                self.static_db[self.collection_name].update_one(
                    filter={
                        '_id': curr_combination_id
                    },
                    update={
                        '$setOnInsert': combination
                    },
                    upsert=True
                )
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: cannot initialize static DB: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            raise DatabaseError()
        finally:
            del combinations

    def initiate_cursor(self):
        self.close_cursor()
        self.dynamic_combinations_cursor = self.static_db[self.collection_name].find()

    def close_cursor(self):
        if self.dynamic_combinations_cursor:
            self.dynamic_combinations_cursor.close()
        self.dynamic_combinations_cursor = None

    def get_next_combination(self):
        try:
            return self.dynamic_combinations_cursor.next()
        except StopIteration as ex:
            logger.info_error("There are no more combinations!")
            return None
        except Exception as ex:
            logger.info_error(f"Execption at {Database.__name__}: get_next_combination")
            raise

    def has_next_combination(self):
        if not self.dynamic_combinations_cursor:
            self.initiate_cursor()
        has_next = self.dynamic_combinations_cursor and self.dynamic_combinations_cursor.alive
        if not has_next:
            self.close_cursor()
        return has_next

    def insert_new_combination(self, combination_result):
        try:
            self.dynamic_db[self.collection_name].insert_one(combination_result)
            return True
        except Exception as e:
            logger.info_error(f'{Database.__name__} cannot update dynamic DB: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            return False

    def delete_combination(self, combination_id):
        try:
            self.dynamic_db[self.collection_name].delete_one({"_id": combination_id})
            return True
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: Could not delete combination: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            return False

    def find_optimal_loop_combination(self, file_id_by_rel_path, loop_label):
        best_speedup = 1
        best_combination_id = self.SERIAL_COMBINATION_ID
        best_loop = None
        loop_is_dead_code = True
        file_is_dead_code = True
        combinations = self.dynamic_db[self.collection_name].find({})
        for combination in combinations:
            if 'error' not in combination.keys():
                for file in combination['run_time_results']:
                    if file['file_id_by_rel_path'] == file_id_by_rel_path:
                        if 'dead_code_file' in file.keys():
                            file_is_dead_code = file_is_dead_code and True
                            break
                        else:
                            file_is_dead_code = False
                            for loop in file['loops']:
                                if loop['loop_label'] == loop_label:
                                    if 'dead_code' in loop.keys():
                                        loop_is_dead_code = loop_is_dead_code and True
                                    else:
                                        loop_is_dead_code = False
                                        if combination['_id'] == Database.SERIAL_COMBINATION_ID and not best_loop \
                                                and best_combination_id == Database.SERIAL_COMBINATION_ID:
                                            best_loop = loop
                                        if loop['speedup'] > best_speedup:
                                            best_speedup = loop['speedup']
                                            best_combination_id = combination['_id']
                                            best_loop = loop
                                    break
                            break
        del combinations
        if file_is_dead_code:
            raise DeadCodeFile(f'file {file_id_by_rel_path} is dead code!')
        if loop_is_dead_code:
            raise DeadCodeLoop(f'Loop {loop_label} in file {file_id_by_rel_path} is dead code!')
        if not best_loop:
            raise MissingDataError(f'Cannot find any loop in db, loop: {loop_label}, file: {file_id_by_rel_path}')
        return best_combination_id, best_loop

    def get_combination_from_static_db(self, combination_id):
        combination = None
        if combination_id == self.SERIAL_COMBINATION_ID:
            return {
                "_id": Database.SERIAL_COMBINATION_ID,
                "compiler_name": Database.SERIAL_COMPILER_NAME,
                "parameters": {
                    "env_params": [],
                    "code_params": [],
                    "compilation_params": []
                }
            }
        try:
            combination = self.static_db[self.collection_name].find_one({"_id": combination_id})
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: Could not find combination: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
        finally:
            return combination

    def get_total_runtime_best_combination(self):
        best_combination = self.dynamic_db[self.collection_name].find_one(
            {"$and": [{"error": {"$exists": False}}, {"total_run_time": {"$ne": Job.RUNTIME_ERROR}}]},
            sort=[("total_run_time", 1)])
        if not best_combination:
            raise NoOptimalCombinationError("All Compar combinations finished with error.")
        return best_combination["_id"]

    def remove_unused_data(self, combination_id):
        self.dynamic_db[self.collection_name].update({"_id": combination_id}, {'$unset': {'run_time_results': ""}})

    def set_error_in_combination(self, combination_id, error):
        self.dynamic_db[self.collection_name].update_one(
            filter={
                '_id': combination_id,
            },
            update={
                '$set': {
                    'error': error
                }
            }
        )

    @staticmethod
    def generate_combination_id(combination):
        fields = [f'compiler_name:{combination["compiler_name"]}']
        env_params = combination['parameters']['env_params']
        for env_param in env_params:
            fields.append(f'env_params:{env_param}')
        code_params = combination['parameters']['code_params']
        for code_param in code_params:
            fields.append(f'code_params:{code_param}')
        compilation_params = combination['parameters']['compilation_params']
        for compilation_param in compilation_params:
            fields.append(f'compilation_params:{compilation_param}')
        fields.sort()
        return hashlib.sha3_384(str(fields).encode()).hexdigest()


def generate_combinations():
    env_params = []
    combinations = []
    with open(ENVIRONMENT_PARAMS_FILE_PATH, 'r') as f:
        env_array = json_util.loads(f.read())
        for param in env_array:
            env_params.append(generate_env_params(param))
        env_params = mult_lists(env_params)

    with open(COMPILATION_PARAMS_FILE_PATH, 'r') as f:
        comb_array = json_util.loads(f.read())
        for comb in comb_array:
            compiler = comb["compiler"]
            essential_valued_params_list = generate_valued_params_list(comb["essential_params"]["valued"], True)
            essential_valued_params_list = mult_lists(essential_valued_params_list)
            essential_toggle_params_list = generate_toggle_params_list(comb["essential_params"]["toggle"], True)
            essential_toggle_params_list = mult_lists(essential_toggle_params_list)

            optional_valued_params_list = generate_valued_params_list(comb["optional_params"]["valued"])
            optional_valued_params_list = mult_lists(optional_valued_params_list)
            optional_toggle_params_list = generate_toggle_params_list(comb["optional_params"]["toggle"])
            optional_toggle_params_list = mult_lists(optional_toggle_params_list)

            all_combs = [essential_valued_params_list, essential_toggle_params_list, optional_valued_params_list,
                         optional_toggle_params_list]
            all_combs = [x for x in all_combs if x != []]
            all_combs = mult_lists(all_combs)

            for compile_comb in all_combs:
                for env_comb in env_params:
                    if not env_comb:
                        curr_env_comb = []
                    else:
                        curr_env_comb = env_comb.split(" ")
                    if not compile_comb:
                        curr_compile_comb = []
                    else:
                        curr_compile_comb = compile_comb.split(" ")
                    new_comb = {
                        "compiler_name": compiler,
                        "parameters": {
                            "env_params": curr_env_comb,
                            "code_params": [],
                            "compilation_params": curr_compile_comb
                        }
                    }
                    combinations.append(new_comb)
        return combinations


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


def generate_env_params(param):
    if not param:
        return [""]
    lst = []
    param_name = param["param"]
    for val in param["vals"]:
        lst.append(f"{param_name}({val});")
    return lst


def mult_lists(lst):
    mult_list = []
    for i in itertools.product(*lst):
        i = list(filter(None, list(i)))  # remove white spaces
        mult_list.append(" ".join(i))
    return mult_list
