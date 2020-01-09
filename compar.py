import os

from combination import Combination
from compilers.autopar import Autopar
from compilers.cetus import Cetus
from compilers.par4all import Par4all
from compilers.gcc import Gcc
from compilers.icc import Icc
from exceptions import UserInputError
from executor import Executor
from job import Job
from fragmentator import Fragmentator
import shutil

from parameters import Parameters
from timer import Timer
import exceptions as e
from database import Database


class Compar:
    GCC = 'gcc'
    ICC = 'icc'
    BACKUP_FOLDER_NAME = "backup"
    ORIGINAL_FILES_FOLDER_NAME = "original_files"
    COMBINATIONS_FOLDER_NAME = "combinations"
    LOGS_FOLDER_NAME = 'logs'

    @staticmethod
    def inject_c_code_to_loop(c_file_path, loop_id, c_code_to_inject):
        e.assert_file_exist(c_file_path)
        with open(c_file_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        loop_id_with_inject_code = loop_id + '\n' + c_code_to_inject
        c_code = c_code.replace(loop_id, loop_id_with_inject_code)
        try:
            with open(c_file_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))

    def __init__(self,
                 working_directory,
                 input_dir,
                 binary_compiler_type,
                 binary_compiler_version,
                 makefile_name="",
                 makefile_parameters=[],
                 makefile_output_files="",
                 is_make_file=False,
                 binary_compiler_flags="",
                 par4all_flags="",
                 autopar_flags="",
                 cetus_flags="",
                 main_file_name="",
                 main_file_parameters="",
                 slurm_parameters=""):

        self.binary_compiler_version = binary_compiler_version
        self.binary_compiler = None
        self.run_time_serial_results = {}
        self.jobs = []
        self.timer = None
        self.db = Database(self.__extract_working_directory_name())
        self.__max_combinations_at_once = 20
        self.__combinations_jobs_to_do = []

        # Build compar environment-----------------------------------
        self.working_directory = working_directory
        self.backup_files_dir = os.path.join(working_directory, Compar.BACKUP_FOLDER_NAME)
        self.original_files_dir = os.path.join(working_directory, Compar.ORIGINAL_FILES_FOLDER_NAME)
        self.combinations_dir = os.path.join(working_directory, Compar.COMBINATIONS_FOLDER_NAME)
        self.logs_dir = os.path.join(working_directory, Compar.LOGS_FOLDER_NAME)
        self.__create_directories_structure(input_dir)
        # -----------------------------------------------------------

        # Creating compiler variables----------------------------------
        # TODO -fix version
        version = ""  # don't know if getting this from the user
        self.relative_c_file_list = Compar.make_relative_c_file_list(self.original_files_dir)
        self.binary_compiler_type = binary_compiler_type
        self.par4all_compiler = Par4all(version, par4all_flags)
        self.autopar_compiler = Autopar(version, autopar_flags)
        self.cetus_compiler = Cetus(version, cetus_flags)
        # -----------------------------------------------------------

        # Saves compiler flags---------------------------------------
        self.user_par4all_flags = par4all_flags
        self.user_autopar_flags = autopar_flags
        self.user_cetus_flags = cetus_flags
        self.user_binary_compiler_flags = binary_compiler_flags
        # -----------------------------------------------------------

        # Makefile---------------------------------------------------
        self.is_make_file = is_make_file
        self.makefile_name = makefile_name
        self.makefile_parameters = makefile_parameters
        self.makefile_output_files = makefile_output_files
        # -----------------------------------------------------------

        # Main file--------------------------------------------------
        self.main_file_name = main_file_name
        self.main_file_parameters = main_file_parameters
        # ----------------------------------------------------------

        # SLURM------------------------------------------------------
        self.slurm_parameters = slurm_parameters
        # ----------------------------------------------------------
        self.files_loop_dict = {}

    def generate_optimal_code(self):
        labels = []
        optimal_loop_ids = []
        optimal_combinations = []

        original_files_path_dict = make_absolute_file_list()

        for file in self.files_loop_dict.items():
            for loop_id in range (file["num_of_loops"]):
                start_label = Fragmentator.get_start_label()+str(loop_id)
                end_label = Fragmentator.get_end_label()+str(loop_id)
                labels.append((start_label,end_label)) #Tuple

                current_optimal_id = self.db.find_optimal_loop_combination(file['file_name'],start_label)
                optimal_loop_ids.append(current_optimal_id)

                current_optimal_combination = self.__combination_json_to_obj(self.db.get_combination_from_static_db(current_optimal_id))
                optimal_combinations.append(current_optimal_combination)



            file_full_path = self.get_file_full_path_from_c_files_list_by_file_name(file['file_name']) #Will be replaced
            #get file with injected ids/times from injected files path

            for index,optimal_combination in optimal_combinations:
                c_code_to_inject = Compar.create_c_code_to_inject(optimal_combinations.get_parameters())

                #Parallelize before injection
                label = labels[index][0]
                Compar.inject_c_code_to_loop(file_full_path,label,c_code_to_inject)

            labels = []
            optimal_loop_ids = []
            optimal_combinations = []

    @staticmethod
    def create_c_code_to_inject(parameters,option):
        if(option == "code"):
            params = parameters.get_code_params()
        else:
            params = parameters.get_env_params()

        c_code = ""
        for param in params:
            c_code += param + ";" + "\n"
        return c_code


    def get_binary_compiler_version(self):
        return self.binary_compiler_version

    def get_binary_compiler(self):
        return self.binary_compiler

    def get_run_time_serial_results(self):
        return self.run_time_serial_results

    def get_runtime_from_run_time_serial_results(self, file_name, loop_label):
        key = file_name, loop_label
        value = self.run_time_serial_results.get(key)
        if value:
            return value
        else:
            raise UserInputError('The input key does not exist')

    def get_jobs(self):
        return self.jobs

    def get_working_directory(self):
        return self.working_directory

    def get_backup_files_dir(self):
        return self.backup_files_dir

    def get_original_files_dir(self):
        return self.original_files_dir

    def get_combinations_dir(self):
        return self.combinations_dir

    def get_relative_c_files_list(self):
        return self.relative_c_file_list

    def get_file_relative_path_from_c_files_list_by_file_name(self, file_name):
        for file in self.relative_c_file_list:
            if file['file_name'] == file_name:
                return file['file_relative_path']
        raise UserInputError("File name: " + str(file_name) + " does not exist.")

    def get_file_name_from_c_files_list_by_file_relative_path(self, file_relative_path):
        for file in self.relative_c_file_list:
            if file['file_relative_path'] == file_relative_path:
                return file['file_name']
        raise UserInputError("File full path: " + str(file_relative_path) + " does not exist.")

    def get_file_name_file_relative_path_from_c_files_list_by_file_name(self, file_name):
        for file in self.relative_c_file_list:
            if file['file_name'] == file_name:
                return file
        raise UserInputError("File name: " + str(file_name) + " does not exist.")

    def get_binary_compiler_type(self):
        return self.binary_compiler_type

    def get_par4all_compiler(self):
        return self.par4all_compiler

    def get_autopar_compiler(self):
        return self.autopar_compiler

    def get_cetus_compiler(self):
        return self.cetus_compiler

    def get_user_par4all_flags(self):
        return self.user_par4all_flags

    def get_user_autopar_flags(self):
        return self.user_autopar_flags

    def get_user_cetus_flags(self):
        return self.user_cetus_flags

    def get_user_binary_compiler_flags(self):
        return self.user_binary_compiler_flags

    def get_is_make_file(self):
        return self.is_make_file

    def get_makefile_name(self):
        return self.makefile_name

    def get_makefile_parameters(self):
        return self.makefile_parameters

    def get_makefile_output_files(self):
        return self.makefile_output_files

    def get_main_file_name(self):
        return self.main_file_name

    def get_main_file_parameters(self):
        return self.main_file_parameters

    def get_slurm_parameters(self):
        return self.slurm_parameters

    def set_binary_compiler_version(self, binary_compiler_version):
        self.binary_compiler_version = binary_compiler_version

    def set_binary_compiler(self, binary_compiler):
        self.binary_compiler = binary_compiler

    def set_run_time_serial_results(self, run_time_serial_results):
        self.run_time_serial_results = run_time_serial_results

    def set_runtime_from_run_time_serial_results(self, file_name, loop_label, runtime):
        key = file_name, loop_label
        self.run_time_serial_results[key] = runtime

    def set_jobs(self, jobs):
        self.jobs = jobs

    def set_working_directory(self, working_directory):
        self.working_directory = working_directory

    def set_backup_files_dir(self, backup_files_dir):
        self.backup_files_dir = backup_files_dir

    def set_original_files_dir(self, original_files_dir):
        self.original_files_dir = original_files_dir

    def set_combinations_dir(self, combinations_dir):
        self.combinations_dir = combinations_dir

    def set_relative_c_file_list(self, relative_c_file_list):
        self.relative_c_file_list = relative_c_file_list

    def set_file_relative_path_from_c_files_list_by_file_name(self, file_name, file_relative_path):
        for file in self.relative_c_file_list:
            if file['file_name'] == file_name:
                file['file_relative_path'] = file_relative_path
        self.relative_c_file_list.append({"file_name": file_name, "file_relative_path": file_relative_path})

    def set_file_name_from_c_files_list_by_file_relative_path(self, file_relative_path, file_name):
        for file in self.relative_c_file_list:
            if file['file_relative_path'] == file_relative_path:
                file['file_name'] = file_name
        self.relative_c_file_list.append({"file_name": file_name, "file_relative_path": file_relative_path})

    def set_binary_compiler_type(self, binary_compiler_type):
        self.binary_compiler_type = binary_compiler_type

    def set_par4all_compiler(self, par4all_compiler):
        self.par4all_compiler = par4all_compiler

    def set_autopar_compiler(self, autopar_compiler):
        self.autopar_compiler = autopar_compiler

    def set_cetus_compiler(self, cetus_compiler):
        self.cetus_compiler = cetus_compiler

    def set_user_par4all_flags(self, user_par4all_flags):
        self.user_par4all_flags = user_par4all_flags

    def set_user_autopar_flags(self, user_autopar_flags):
        self.user_autopar_flags = user_autopar_flags

    def set_user_cetus_flags(self, user_cetus_flags):
        self.user_cetus_flags = user_cetus_flags

    def set_user_binary_compiler_flags(self, user_binary_compiler_flags):
        self.user_binary_compiler_flags = user_binary_compiler_flags

    def set_is_make_file(self, is_make_file):
        self.is_make_file = is_make_file

    def set_makefile_name(self):
        return self.makefile_name

    def set_makefile_parameters(self, makefile_parameters):
        self.makefile_parameters = makefile_parameters

    def set_makefile_output_files(self, makefile_output_files):
        self.makefile_output_files = makefile_output_files

    def set_main_file_name(self, main_file_name):
        self.main_file_name = main_file_name

    def set_main_file_parameters(self, main_file_parameters):
        self.main_file_parameters = main_file_parameters

    def set_slurm_parameters(self, slurm_parameters):
        self.slurm_parameters = slurm_parameters

    @staticmethod
    def __combination_json_to_obj(combination_json):
        parameters_json = combination_json['parameters']
        parameters_obj = Parameters(code_params=parameters_json['code_params'],
                                    env_params=parameters_json['env_params'],
                                    compilation_params=parameters_json['compilation_params'])
        combination_obj = Combination(combination_id=combination_json['_id'],
                                      compiler_name=combination_json['compiler_name'],
                                      parameters=parameters_obj)
        return combination_obj

    def __extract_working_directory_name(self):
        working_directory_name = self.working_directory
        if not os.path.isdir(working_directory_name):
            raise UserInputError('Working Directory variable is not a directory')
        if working_directory_name.endswith(os.path.sep):
            working_directory_name = os.path.split(working_directory_name)[0]  # remove the suffix separator
        return os.path.basename(working_directory_name)

    def __get_parallel_compiler_by_name(self, compiler_name):
        compilers_map = {
            'autopar': self.autopar_compiler,
            'cetus': self.cetus_compiler,
            'par4all': self.par4all_compiler,
        }
        return compilers_map[compiler_name]

    def run_parallel_combinations(self):  # TODO: review all function
        while self.db.has_next_combination():
            combination_obj = self.__combination_json_to_obj(self.db.get_next_combination())
            combination_folder_path = self.create_combination_folder(str(combination_obj.get_combination_id()))
            parallel_compiler = self.__get_parallel_compiler_by_name(combination_obj.get_compiler())
            # TODO: combine the user flags with combination flags (we want to let the user to insert his flags??)
            # TODO: initiate_for_new_task
            # parallel_compiler.set_compilation_flags(combination_obj.get_parameters().get_compilation_params())
            # TODO: continue

    def __create_directories_structure(self, input_dir):
        os.makedirs(self.original_files_dir, exist_ok=True)
        os.makedirs(self.combinations_dir, exist_ok=True)
        os.makedirs(self.backup_files_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        if os.path.isdir(input_dir):
            self.__copy_folder_content(input_dir, self.original_files_dir)
            self.__copy_folder_content(input_dir, self.backup_files_dir)
        else:
            raise UserInputError('The input path must be directory')

    @staticmethod
    def __copy_folder_content(src, dst):
        for path in os.listdir(src):
            if os.path.isfile(path):
                shutil.copy(path, dst)
            elif os.path.isdir(path):
                shutil.copytree(path, dst)

    def __copy_sources_to_combination_folder(self, combination_folder_path):
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)

    @staticmethod
    def __delete_combination_folder(combination_folder_path):
        shutil.rmtree(combination_folder_path)

    @staticmethod
    def make_relative_c_file_list(base_dir):
        file_list = []
        for path, dirs, files in os.walk(base_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.c':
                    relative_path = os.path.relpath(os.path.join(path, file), base_dir)
                    file_list.append({"file_name": file, "file_relative_path": relative_path})
        return file_list

    def make_absolute_file_list(self, base_dir_path):
        return list(map(lambda file_dict: {'file_name': file_dict['file_name'],
                                           'file_full_path': os.path.join(base_dir_path,
                                                                          file_dict['file_relative_path'])
                                           }, self.relative_c_file_list))

    def __run_binary_compiler(self, serial_dir_path):
        # TODO: make the method more generic (like parallel compiler)
        if self.binary_compiler_type == Compar.ICC:
            self.binary_compiler = Icc(self.binary_compiler_version, self.user_binary_compiler_flags,
                                       serial_dir_path, self.main_file_name)
        elif self.binary_compiler_type == Compar.GCC:
            self.binary_compiler = Gcc(self.binary_compiler_version, self.user_binary_compiler_flags,
                                       serial_dir_path, self.main_file_name)
        self.binary_compiler.compile()

    def run_serial(self):
        serial_dir_path = os.path.join(self.combinations_dir, 'serial')
        shutil.rmtree(serial_dir_path, ignore_errors=True)
        os.mkdir(serial_dir_path)
        self.__copy_sources_to_combination_folder(serial_dir_path)

        if self.is_make_file:
            pass
        else:
            self.__run_binary_compiler(serial_dir_path)

        combination = Combination('0', self.binary_compiler_type, None)
        job = Job(serial_dir_path, self.main_file_parameters, combination)
        Executor.execute_jobs([job])  # TODO: check how to detect the dir name - remove os.walk()

        # update run_time_serial_results
        for file in self.make_absolute_file_list(serial_dir_path):
            run_time_result_loops = job.get_file_results_loops(file['file_name'])
            for loop in run_time_result_loops:
                key = file['file_name'], loop['loop_label']
                value = loop['run_time']
                self.run_time_serial_results[key] = value

            # update database
            #  TODO: add speedup 1 to all the serial loops
            self.db.insert_new_combination(job.get_job_results())

        self.__delete_combination_folder(serial_dir_path)

    def fragment_and_add_timers(self):
        for c_file_dict in self.make_absolute_file_list(self.original_files_dir):
            try:
                self.timer = Timer(c_file_dict['file_full_path'])
                self.timer.inject_timers()
            except e.FileError as err:
                print(str(err))

    def create_combination_folder(self, combination_folder_name):
        combination_folder_path = os.path.join(self.combinations_dir, combination_folder_name)
        os.mkdir(combination_folder_path)
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)
        if not os.path.isdir(combination_folder_path):
            raise e.FolderError(f'Cannot create {combination_folder_path} folder')
        return combination_folder_path

