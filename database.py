import pymongo
from exceptions import DatabaseError, MissingDataError, DeadCodeLoop, DeadCodeFile, NoOptimalCombinationError
import logger
import traceback
import hashlib
from combinator import generate_combinations
from globals import ComparMode, DatabaseConfig, JobConfig, LogPhrases
import getpass


class Database:

    SERIAL_COMBINATION_ID = DatabaseConfig.SERIAL_COMBINATION_ID
    COMPAR_COMBINATION_ID = DatabaseConfig.COMPAR_COMBINATION_ID
    FINAL_RESULTS_COMBINATION_ID = DatabaseConfig.FINAL_RESULTS_COMBINATION_ID
    COMBINATIONS_DB, RESULTS_DB = 0, 1

    @staticmethod
    def generate_combination_id(combination: dict):
        fields = [f'compiler_name:{combination["compiler_name"]}']
        omp_rtl_params = combination['parameters']['omp_rtl_params']
        for omp_rtl_param in omp_rtl_params:
            fields.append(f'omp_rtl_params:{omp_rtl_param}')
        omp_directives_params = combination['parameters']['omp_directives_params']
        for omp_directives_param in omp_directives_params:
            fields.append(f'omp_directives_params:{omp_directives_param}')
        compilation_params = combination['parameters']['compilation_params']
        for compilation_param in compilation_params:
            fields.append(f'compilation_params:{compilation_param}')
        fields.sort()
        return hashlib.sha3_384(str(fields).encode()).hexdigest()

    @staticmethod
    def __get_collection_name(project_name):
        collection_name = f"{getpass.getuser()}_{project_name}"
        static_namespace = f'{DatabaseConfig.STATIC_DB_NAME}.{collection_name}'
        dynamic_namespace = f'{DatabaseConfig.DYNAMIC_DB_NAME}.{collection_name}'
        longer_namespace = max((static_namespace, dynamic_namespace), key=len)
        if len(longer_namespace) > DatabaseConfig.NAMESPACE_LENGTH_LIMIT:
            new_name = longer_namespace[:DatabaseConfig.NAMESPACE_LENGTH_LIMIT].split('.')[1]
            logger.info_error(f'DB namespace is too long! (max is {DatabaseConfig.NAMESPACE_LENGTH_LIMIT} characters)')
            logger.info_error(f'The name was changed from {collection_name} to {new_name}')
            collection_name = new_name
        return collection_name

    def __init__(self, project_name, mode):
        self.mode = mode
        self.collection_name = Database.__get_collection_name(project_name)
        try:
            self.connection = pymongo.MongoClient(DatabaseConfig.SERVER_ADDRESS)
            self.static_db = self.connection[DatabaseConfig.STATIC_DB_NAME]
            self.dynamic_db = self.connection[DatabaseConfig.DYNAMIC_DB_NAME]
            self.num_of_combinations = 0
        except Exception as e:
            raise DatabaseError(str(e) + "\nDatabase connection failed!")

        if self.mode == ComparMode.OVERWRITE:
            if self.is_collection_exists(self.collection_name, Database.RESULTS_DB):
                self.dynamic_db.drop_collection(self.collection_name)
        elif self.mode == ComparMode.NEW:
            if self.is_collection_exists(self.collection_name, Database.RESULTS_DB):
                self.collection_name = self.get_new_collection_name(self.collection_name)
                logger.info(f'Project name changed from {project_name} to {self.get_project_name()}')

    def get_project_name(self):
        if '_' in self.collection_name:
            return self.collection_name.split('_', 1)[1]
        else:
            return self.collection_name

    def get_new_collection_name(self, original_collection_name: str):
        i = 1
        while self.is_collection_exists(f"{original_collection_name}_{i}", Database.RESULTS_DB):
            i = i + 1
        return f"{original_collection_name}_{i}"

    def create_collections(self):
        logger.info(f'Initializing {self.collection_name} databases')
        try:
            self.create_static_db()
            self.create_dynamic_db()
        except Exception as e:
            raise DatabaseError(str(e) + "\nFailed to initialize DB!")

    def create_static_db(self):
        if self.is_collection_exists(self.collection_name, Database.COMBINATIONS_DB):
            self.static_db.drop_collection(self.collection_name)
        self.static_db.create_collection(self.collection_name)
        num_of_parallel_combinations = self.initialize_static_db()
        self.num_of_combinations = num_of_parallel_combinations + 2  # serial + parallel + final
        logger.info(LogPhrases.TOTAL_COMBINATIONS.format(self.num_of_combinations))

    def create_dynamic_db(self):
        if self.mode != ComparMode.CONTINUE:
            self.dynamic_db.create_collection(self.collection_name)
        else:
            ids_in_static = [comb['_id'] for comb in self.static_db[self.collection_name].find({}, {"_id": 1})]
            ids_in_dynamic = [comb['_id'] for comb in self.dynamic_db[self.collection_name].find({}, {"_id": 1})]
            old_ids = [comb_id for comb_id in ids_in_dynamic if comb_id not in
                       ids_in_static + [self.SERIAL_COMBINATION_ID]]
            self.dynamic_db[self.collection_name].delete_many({'_id': {'$in': old_ids}})
            del ids_in_static, ids_in_dynamic, old_ids
            self.dynamic_db[self.collection_name].delete_one({'_id': Database.COMPAR_COMBINATION_ID})
            self.dynamic_db[self.collection_name].delete_one({'_id': Database.FINAL_RESULTS_COMBINATION_ID})
            self.dynamic_db[self.collection_name].delete_many({"error": {"$exists": True}})

    def is_collection_exists(self, collection_name: str, database: int = RESULTS_DB):
        if database == Database.COMBINATIONS_DB:
            database_object = self.static_db
        elif database == Database.RESULTS_DB:
            database_object = self.dynamic_db
        else:
            raise ValueError(f'Unknown value {database}')
        return collection_name in database_object.list_collection_names()

    def initialize_static_db(self):
        try:
            combinations = generate_combinations()
            num_of_parallel_combinations = len(combinations)
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
            return num_of_parallel_combinations
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: cannot initialize static DB: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            raise DatabaseError()
        finally:
            del combinations

    def close_connection(self):
        self.connection.close()

    def combination_has_results(self, combination_id: str):
        return self.get_combination_results(combination_id) is not None

    def combinations_iterator(self):
        try:
            for combination in self.static_db[self.collection_name].find():
                if self.combination_has_results(combination['_id']):
                    continue
                yield combination
        except Exception:
            logger.info_error(f"Exception at {Database.__name__}: get_next_combination")
            raise

    def insert_new_combination_results(self, combination_result: dict):
        try:
            self.dynamic_db[self.collection_name].insert_one(combination_result)
            return True
        except Exception as e:
            logger.info_error(f'{Database.__name__}: cannot update dynamic DB: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            return False

    def delete_combination(self, combination_id: str):
        try:
            self.dynamic_db[self.collection_name].delete_one({"_id": combination_id})
            return True
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: Could not delete combination: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
            return False

    def find_optimal_loop_combination(self, file_id_by_rel_path: str, loop_label: str):
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

    def get_combination_results(self, combination_id: str):
        combination = None
        try:
            combination = self.dynamic_db[self.collection_name].find_one({"_id": combination_id})
        except Exception as e:
            logger.info_error(f'Exception at {Database.__name__}: Could not find results for combination: {e}')
            logger.debug_error(f'{traceback.format_exc()}')
        finally:
            return combination

    def get_combination_from_static_db(self, combination_id: str):
        combination = None
        if combination_id == self.SERIAL_COMBINATION_ID:
            return {
                "_id": Database.SERIAL_COMBINATION_ID,
                "compiler_name": Database.SERIAL_COMBINATION_ID,
                "parameters": {
                    "omp_rtl_params": [],
                    "omp_directives_params": [],
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
            {"$and": [{"error": {"$exists": False}}, {"total_run_time": {"$ne": JobConfig.RUNTIME_ERROR}}]},
            sort=[("total_run_time", 1)])
        if not best_combination:
            raise NoOptimalCombinationError("All Compar combinations finished with error.")
        return best_combination["_id"]

    def remove_unused_data(self, combination_id: str):
        self.dynamic_db[self.collection_name].update({"_id": combination_id}, {'$unset': {'run_time_results': ""}})

    def set_error_in_combination(self, combination_id: str, error: str):
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

    def delete_all_related_collections(self):
        if self.collection_name in self.static_db.list_collection_names():
            self.static_db.drop_collection(self.collection_name)
        if self.collection_name in self.dynamic_db.list_collection_names():
            self.dynamic_db.drop_collection(self.collection_name)

    def get_final_result_speedup_and_runtime(self):
        serial_results = self.get_combination_results(Database.SERIAL_COMBINATION_ID)
        final_results = self.get_combination_results(Database.FINAL_RESULTS_COMBINATION_ID)
        speedup = float(serial_results['total_run_time']) / float(final_results['total_run_time'])
        return speedup, float(final_results['total_run_time'])
