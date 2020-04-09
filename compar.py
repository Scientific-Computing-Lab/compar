import os
import re
from time import sleep

from combination import Combination
from compilers.autopar import Autopar
from compilers.cetus import Cetus
from compilers.par4all import Par4all
from compilers.gcc import Gcc
from compilers.icc import Icc
from exceptions import UserInputError
from executor import Executor
from file_formator import format_c_code
from job import Job
from fragmentator import Fragmentator
import shutil
import csv
from exceptions import FileError
from exceptions import CompilationError
from exceptions import ExecutionError
from parameters import Parameters
from timer import Timer
import exceptions as e
from database import Database
from compilers.makefile import Makefile
import traceback
import logger


class Compar:
    GCC = 'gcc'
    ICC = 'icc'
    PAR4ALL = 'par4all'
    CETUS = 'cetus'
    AUTOPAR = 'autopar'
    BACKUP_FOLDER_NAME = "backup"
    ORIGINAL_FILES_FOLDER_NAME = "original_files"
    COMBINATIONS_FOLDER_NAME = "combinations"
    LOGS_FOLDER_NAME = 'logs'
    SUMMARY_FILE_NAME = 'summary.csv'
    NUM_OF_THREADS = 4

    @staticmethod
    def replace_labels(file_path, num_of_loops):
        with open(file_path, 'r+') as f:
            content = f.read()
            for loop_id in range(1, num_of_loops + 1):
                old_start_label = '/* ' + Fragmentator.get_start_label()[3:] + str(loop_id) + ' */'
                new_start_label = Fragmentator.get_start_label() + str(loop_id)
                old_end_label = '/* ' + Fragmentator.get_end_label()[3:] + str(loop_id) + ' */'
                new_end_label = Fragmentator.get_end_label() + str(loop_id)
                content = content.replace(old_start_label, new_start_label)
                content = content.replace(old_end_label, new_end_label)
            f.seek(0)
            f.write(content)
            f.truncate()

    @staticmethod
    def inject_c_code_to_loop(c_file_path, loop_id, c_code_to_inject):
        e.assert_file_exist(c_file_path)
        with open(c_file_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        loop_id_with_inject_code = loop_id + '\n' + c_code_to_inject
        c_code = re.sub(loop_id + '[ ]*\n', loop_id_with_inject_code, c_code)
        try:
            with open(c_file_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))

    @staticmethod
    def __copy_pips_stubs_to_folder(destination_folder_path):
        pips_stubs_name = 'pips_stubs.c'
        if pips_stubs_name not in os.listdir(destination_folder_path):
            pips_stubs_path = os.path.join('assets', pips_stubs_name)
            shutil.copy(pips_stubs_path, destination_folder_path)

    @staticmethod
    def format_c_files(list_of_file_paths):
        for file_path in list_of_file_paths:
            format_c_code([file_path, ])

    def __init__(self,
                 working_directory,
                 input_dir,
                 main_file_rel_path,
                 binary_compiler_type="",
                 binary_compiler_version=None,
                 binary_compiler_flags=None,
                 save_combinations_folders=False,
                 is_make_file=False,
                 makefile_commands=None,
                 makefile_exe_folder_rel_path="",
                 makefile_output_exe_file_name="",
                 ignored_rel_paths=None,
                 par4all_flags=None,
                 autopar_flags=None,
                 cetus_flags=None,
                 include_dirs_list=None,
                 main_file_parameters=None,
                 slurm_parameters=None,
                 is_nas=False,
                 time_limit=None,
                 slurm_partition='grid'):

        if not is_make_file:
            e.assert_only_files(input_dir)
        if not include_dirs_list:
            include_dirs_list = []
        if not makefile_commands:
            makefile_commands = []
        if not binary_compiler_flags:
            binary_compiler_flags = []
        if not par4all_flags:
            par4all_flags = []
        if not autopar_flags:
            autopar_flags = []
        if not cetus_flags:
            cetus_flags = []
        if not main_file_parameters:
            main_file_parameters = []
        if not slurm_parameters:
            slurm_parameters = []
        if not ignored_rel_paths:
            ignored_rel_paths = []

        self.serial_run_time = {}
        self.main_file_rel_path = main_file_rel_path
        self.save_combinations_folders = save_combinations_folders
        self.binary_compiler = None
        self.binary_compiler_version = binary_compiler_version
        self.jobs = []
        self.__timer = None
        self.__max_combinations_at_once = 20
        self.ignored_rel_paths = ignored_rel_paths
        self.include_dirs_list = include_dirs_list
        self.is_nas = is_nas
        self.time_limit = time_limit
        self.slurm_partition = slurm_partition

        # Build compar environment-----------------------------------
        e.assert_forbidden_characters(working_directory)
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
        self.relative_c_file_list = self.make_relative_c_file_list(self.original_files_dir)
        self.binary_compiler_type = binary_compiler_type
        self.par4all_compiler = Par4all(version, par4all_flags, include_dirs_list=self.include_dirs_list, is_nas=is_nas)
        self.autopar_compiler = Autopar(version, autopar_flags, include_dirs_list=self.include_dirs_list)
        self.cetus_compiler = Cetus(version, cetus_flags, include_dirs_list=self.include_dirs_list)
        # -----------------------------------------------------------

        # Saves compiler flags---------------------------------------
        self.user_par4all_flags = par4all_flags
        self.user_autopar_flags = autopar_flags
        self.user_cetus_flags = cetus_flags
        self.user_binary_compiler_flags = binary_compiler_flags
        # -----------------------------------------------------------

        # Makefile---------------------------------------------------
        self.is_make_file = is_make_file
        self.makefile_commands = makefile_commands
        self.makefile_exe_folder_rel_path = makefile_exe_folder_rel_path
        self.makefile_output_exe_file_name = makefile_output_exe_file_name
        # -----------------------------------------------------------

        # Main file--------------------------------------------------
        self.main_file_parameters = main_file_parameters
        # ----------------------------------------------------------

        # SLURM------------------------------------------------------
        self.slurm_parameters = slurm_parameters
        # ----------------------------------------------------------
        self.files_loop_dict = {}

        # INITIALIZATIONS
        if not is_make_file:
            self.__initialize_binary_compiler()
        self.db = Database(self.__extract_working_directory_name())

    def generate_optimal_code(self):
        compar_combination_folder_name = 'compar_combination'
        final_result_folder_name = 'final_results'
        optimal_loops_data = []

        # copy final results into this folder
        compar_combination_folder_path = self.create_combination_folder(compar_combination_folder_name,
                                                                        base_dir=self.working_directory)
        final_files_list = self.make_absolute_file_list(compar_combination_folder_path)

        for file_id_by_rel_path, loops in self.files_loop_dict.items():
            current_file = {"file_id_by_rel_path": file_id_by_rel_path, 'optimal_loops': []}
            for loop_id in range(1, loops[0]+1):
                start_label = Fragmentator.get_start_label()+str(loop_id)
                end_label = Fragmentator.get_end_label()+str(loop_id)
                try:
                    current_optimal_id, current_loop = self.db.find_optimal_loop_combination(file_id_by_rel_path,
                                                                                             str(loop_id))
                    # update the optimal loops list
                    current_loop['_id'] = current_optimal_id
                    current_file["optimal_loops"].append(current_loop)
                except e.DeadCodeFile:
                    current_file["dead_code_file"] = True
                    break
                except e.DeadCodeLoop:
                    current_file["optimal_loops"].append({'_id': '0', 'loop_label': str(loop_id), 'dead_code': True})
                    current_optimal_id = '0'

                # if the optimal combination is the serial => do nothing
                if current_optimal_id != '0':
                    current_optimal_combination = self.__combination_json_to_obj(
                        self.db.get_combination_from_static_db(current_optimal_id))
                    final_results_folder_path = self.create_combination_folder(
                        "current_combination", base_dir=self.working_directory)
                    files_list = self.make_absolute_file_list(final_results_folder_path)
                    current_comp_name = current_optimal_combination.compiler_name

                    # get direct file path to inject params
                    src_file_path = list(filter(lambda x: x['file_id_by_rel_path'] == file_id_by_rel_path, files_list))
                    src_file_path = src_file_path[0]['file_full_path']

                    # parallelize and inject
                    self.parallel_compilation_of_one_combination(current_optimal_combination, final_results_folder_path)

                    # replace loop in c file using final_files_list
                    target_file_path = list(filter(lambda x: x['file_id_by_rel_path'] == file_id_by_rel_path,
                                                   final_files_list))
                    target_file_path = target_file_path[0]['file_full_path']

                    Compar.replace_loops_in_files(src_file_path, target_file_path, start_label, end_label)
                    Compar.add_to_loop_details_about_comp_and_combination(target_file_path, start_label,
                                                                          current_optimal_id, current_comp_name)
                    sleep(1)  # prevent IO error
                    shutil.rmtree(final_results_folder_path)
            optimal_loops_data.append(current_file)

        # remove timers code
        self.remove_timer_code(compar_combination_folder_path)
        # inject new code
        Timer.inject_timer_to_compar_mixed_file(os.path.join(compar_combination_folder_path,
                                                             self.main_file_rel_path), compar_combination_folder_path)
        # format all optimal files
        self.format_c_files([file_dict['file_full_path'] for file_dict in final_files_list])
        self.generate_summary_file(optimal_loops_data, compar_combination_folder_path)
        try:
            self.compile_combination_to_binary(compar_combination_folder_path, inject=False)
            job = Job(compar_combination_folder_path, Combination(Combination.FINAL_COMBINATION_ID, "mixed", []), [])
            self.jobs.append(job)
            self.run_and_save_job_list()
        except Exception as ex:
            self.save_combination_as_failure(Combination.FINAL_COMBINATION_ID, str(ex) +
                                             'exception in Compar. generate_optimal_code: cannot compile compar' +
                                             'mixed combination code', compar_combination_folder_path)
        # Check for best total runtime
        best_runtime_combination_id = self.db.get_total_runtime_best_combination()
        if best_runtime_combination_id != Combination.FINAL_COMBINATION_ID:
            combination_obj = self.__combination_json_to_obj(
                self.db.get_combination_from_static_db(best_runtime_combination_id))
            final_results_folder_path = self.create_combination_folder(
                final_result_folder_name, self.working_directory)
            try:
                if best_runtime_combination_id != Database.SERIAL_COMBINATION_ID:
                    self.parallel_compilation_of_one_combination(combination_obj, final_results_folder_path)
                self.compile_combination_to_binary(final_results_folder_path)
                self.update_summary_file(combination_obj, compar_combination_folder_path)
                summary_file_path = os.path.join(compar_combination_folder_path, self.SUMMARY_FILE_NAME)
                summary_file_new_path = os.path.join(final_results_folder_path, self.SUMMARY_FILE_NAME)
                shutil.move(summary_file_path, summary_file_new_path)
            except Exception as ex:
                raise Exception(f"Total runtime calculation - The optimal file could not be compiled, combination"
                                f" {best_runtime_combination_id}.\n{ex}")
        else:
            final_folder_path = os.path.join(self.working_directory, final_result_folder_name)
            shutil.copytree(compar_combination_folder_path, final_folder_path, dirs_exist_ok=True)
        self.db.remove_unused_data(Combination.FINAL_COMBINATION_ID)

    @staticmethod
    def get_file_content(file_path):
        try:
            with open(file_path, 'r') as input_file:
                return input_file.read()
        except FileNotFoundError:
            raise FileError(f'File {file_path} not exist')

    @staticmethod
    def add_to_loop_details_about_comp_and_combination(file_path, start_label, combination_id, comp_name):
        e.assert_file_exist(file_path)
        e.assert_file_is_empty(file_path)
        with open(file_path, 'r') as file:
            file_text = file.read()
        to_replace = ''
        to_replace += start_label + '\n'
        to_replace += '// COMBINATION_ID: ' + combination_id + '\n'
        to_replace += '// COMPILER_NAME: ' + comp_name + '\n'
        file_text = re.sub(f'{start_label}[ ]*\\n', to_replace, file_text)
        try:
            with open(file_path, 'w') as file:
                file.write(file_text)
        except OSError as err:
            raise e.FileError(str(err))

    @staticmethod
    def replace_loops_in_files(origin_path, destination_path, start_label, end_label):

        origin_file_string = Compar.get_file_content(origin_path)
        destination_file_string = Compar.get_file_content(destination_path)

        origin_cut_string = re.findall(f'{start_label}[ ]*\\n.*{end_label}[ ]*\\n', origin_file_string, flags=re.DOTALL)
        if len(origin_cut_string) != 1:
            raise Exception(f'cannot find loop {start_label} in {origin_path}')
        origin_cut_string = origin_cut_string[0]

        destination_cut_string = re.findall(f'{start_label}[ ]*\\n.*{end_label}[ ]*\\n', destination_file_string,
                                            flags=re.DOTALL)
        if len(destination_cut_string) != 1:
            raise Exception(f'cannot find loop {start_label} in {destination_path}')
        destination_cut_string = destination_cut_string[0]

        destination_file_string = destination_file_string.replace(destination_cut_string, origin_cut_string)

        with open(destination_path, "w") as input_file:
            input_file.write(destination_file_string)

    @staticmethod
    def create_c_code_to_inject(parameters, option):
        if option == "code":
            params = parameters.get_code_params()
        elif option == "env":
            params = parameters.get_env_params()
        else:
            raise UserInputError(f'The input {option} is not supported')

        c_code = ""
        for param in params:
            if option == "env":
                c_code += param + "\n"
        return c_code

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
            raise UserInputError('The given directory is not a directory')
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

    def __replace_result_file_name_prefix(self, container_folder_path):
        for c_file_dict in self.make_absolute_file_list(container_folder_path):
            with open(c_file_dict['file_full_path'], 'r') as f:
                file_content = f.read()
            old_prefix = Timer.get_file_name_prefix_token()
            new_prefix = os.path.dirname(c_file_dict['file_full_path']) + os.sep
            file_content = file_content.replace(old_prefix, new_prefix)
            with open(c_file_dict['file_full_path'], 'w') as f:
                f.write(file_content)

    def __initialize_binary_compiler(self):
        binary_compilers_map = {
            Compar.ICC: Icc(version=self.binary_compiler_version),
            Compar.GCC: Gcc(version=self.binary_compiler_version)
        }
        self.binary_compiler = binary_compilers_map[self.binary_compiler_type]

    def parallel_compilation_of_one_combination(self, combination_obj, combination_folder_path):
        compiler_name = combination_obj.get_compiler()
        parallel_compiler = self.__get_parallel_compiler_by_name(compiler_name)
        # TODO: combine the user flags with combination flags (we want to let the user to insert his flags??)
        parallel_compiler.initiate_for_new_task(combination_obj.get_parameters().get_compilation_params(),
                                                combination_folder_path,
                                                self.make_absolute_file_list(combination_folder_path))
        if compiler_name == Compar.PAR4ALL:
            if self.is_nas:
                parallel_compiler.set_make_obj(Makefile(combination_folder_path, self.makefile_exe_folder_rel_path,
                                                        self.makefile_output_exe_file_name, self.makefile_commands))
                self.__copy_pips_stubs_to_folder(os.path.join(combination_folder_path, 'common'))
            else:
                self.__copy_pips_stubs_to_folder(combination_folder_path)
        parallel_compiler.compile()
        if compiler_name == Compar.PAR4ALL:
            if self.is_nas:
                os.remove(os.path.join(combination_folder_path, 'common', 'pips_stubs.c'))
            else:
                os.remove(os.path.join(combination_folder_path, 'pips_stubs.c'))
        env_code = self.create_c_code_to_inject(combination_obj.get_parameters(), 'env')
        for file_dict in self.make_absolute_file_list(combination_folder_path):
            if compiler_name == Compar.CETUS:
                self.replace_labels(file_dict['file_full_path'],
                                    self.files_loop_dict[file_dict['file_id_by_rel_path']][0])
            for loop_id in range(1, self.files_loop_dict[file_dict['file_id_by_rel_path']][0] + 1):
                loop_start_label = Fragmentator.get_start_label() + str(loop_id)
                self.inject_c_code_to_loop(file_dict['file_full_path'], loop_start_label, env_code)

    def compile_combination_to_binary(self, combination_folder_path, extra_flags_list=None, inject=True):
        if inject:
            Timer.inject_atexit_code_to_main_file(os.path.join(combination_folder_path, self.main_file_rel_path),
                                                  self.files_loop_dict, combination_folder_path)
        if self.is_make_file:
            makefile = Makefile(combination_folder_path, self.makefile_exe_folder_rel_path,
                                self.makefile_output_exe_file_name, self.makefile_commands)
            makefile.make()
        else:
            compilation_flags = self.user_binary_compiler_flags
            if extra_flags_list:
                compilation_flags += extra_flags_list
            self.binary_compiler.initiate_for_new_task(compilation_flags,
                                                       combination_folder_path,
                                                       self.main_file_rel_path)
            self.binary_compiler.compile()

    def calculate_speedups(self):
        self.db.update_all_speedups()

    def run_and_save_job_list(self):
        job_list = []
        try:
            job_list = Executor.execute_jobs(self.jobs, self.files_loop_dict, self.db, self.relative_c_file_list,
                                             self.slurm_partition, self.NUM_OF_THREADS,
                                             self.slurm_parameters, self.serial_run_time, time_limit=self.time_limit)
        except Exception as ex:
            logger.info_error(f'Exception at {Compar.__name__}: {ex}')
            logger.debug_error(f'{traceback.format_exc()}')
        finally:
            for job in job_list:
                if not self.save_combinations_folders:
                    self.__delete_combination_folder(job.get_directory_path())
            self.jobs.clear()

    def save_combination_as_failure(self, combination_id, error_msg, combination_folder_path):
        combination_dict = {
            '_id': combination_id,
            'error': error_msg
        }
        self.db.insert_new_combination(combination_dict)
        sleep(1)
        if not self.save_combinations_folders:
            self.__delete_combination_folder(combination_folder_path)

    def run_parallel_combinations(self):
        while self.db.has_next_combination():
            if len(self.jobs) >= self.__max_combinations_at_once:
                self.run_and_save_job_list()
            combination_obj = self.__combination_json_to_obj(self.db.get_next_combination())
            combination_folder_path = self.create_combination_folder(str(combination_obj.get_combination_id()))
            try:
                self.parallel_compilation_of_one_combination(combination_obj, combination_folder_path)
                self.compile_combination_to_binary(combination_folder_path)
            except Exception as ex:
                logger.info_error(f'Exception at {Compar.__name__}: {ex}')
                logger.debug_error(f'{traceback.format_exc()}')
                self.save_combination_as_failure(combination_obj.get_combination_id(), str(ex), combination_folder_path)
                continue
            job = Job(combination_folder_path, combination_obj, self.main_file_parameters)
            self.jobs.append(job)
        if self.jobs:
            self.run_and_save_job_list()

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
        for rel_path in os.listdir(src):
            src_full_path = os.path.join(src, rel_path)
            if os.path.isfile(src_full_path):
                shutil.copy(src_full_path, dst)
            elif os.path.isdir(src_full_path):
                dest_path_include_new_dir = os.path.join(dst, rel_path)
                if os.path.exists(dest_path_include_new_dir):
                    shutil.rmtree(dest_path_include_new_dir)
                shutil.copytree(src_full_path, dest_path_include_new_dir)

    def __copy_sources_to_combination_folder(self, combination_folder_path):
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)

    @staticmethod
    def __delete_combination_folder(combination_folder_path):
        shutil.rmtree(combination_folder_path)

    def make_relative_c_file_list(self, base_dir):
        e.assert_forbidden_characters(base_dir)
        file_list = []
        for path, dirs, files in os.walk(base_dir):
            if os.path.relpath(path, base_dir) not in self.ignored_rel_paths:
                for file in files:
                    if os.path.splitext(file)[1] == '.c':
                        relative_path = os.path.relpath(os.path.join(path, file), base_dir)
                        e.assert_forbidden_characters(relative_path)
                        # file_name is not unique!
                        file_list.append({"file_name": file, "file_relative_path": relative_path})
        return file_list

    def make_absolute_file_list(self, base_dir_path):
        return list(map(lambda file_dict: {'file_name': file_dict['file_name'],
                                           'file_full_path': os.path.join(base_dir_path,
                                                                          file_dict['file_relative_path']),
                                           'file_id_by_rel_path': file_dict['file_relative_path']
                                           }, self.relative_c_file_list))

    def __run_binary_compiler(self, serial_dir_path):
        self.binary_compiler.initiate_for_new_task(compilation_flags=self.user_binary_compiler_flags,
                                                   input_file_directory=serial_dir_path,
                                                   main_c_file=self.main_file_rel_path)
        self.binary_compiler.compile()

    def run_serial(self):
        serial_dir_path = os.path.join(self.combinations_dir, 'serial')
        shutil.rmtree(serial_dir_path, ignore_errors=True)
        os.mkdir(serial_dir_path)
        self.__copy_sources_to_combination_folder(serial_dir_path)
        Timer.inject_atexit_code_to_main_file(os.path.join(serial_dir_path, self.main_file_rel_path),
                                                      self.files_loop_dict, serial_dir_path)
        # self.__replace_result_file_name_prefix(serial_dir_path)

        if self.is_make_file:
            compiler_type = "Makefile"
            makefile = Makefile(serial_dir_path, self.makefile_exe_folder_rel_path, self.makefile_output_exe_file_name,
                                self.makefile_commands)
            makefile.make()
        else:
            compiler_type = self.binary_compiler_type
            try:
                self.__run_binary_compiler(serial_dir_path)
            except e.CombinationFailure as ex:
                raise e.CompilationError(str(ex))

        combination = Combination(combination_id=Database.SERIAL_COMBINATION_ID,
                                  compiler_name=compiler_type,
                                  parameters=None)
        job = Job(directory=serial_dir_path,
                  exec_file_args=self.main_file_parameters,
                  combination=combination)

        job = Executor.execute_jobs([job, ], self.files_loop_dict, self.db, self.relative_c_file_list,
                                    self.slurm_partition, self.NUM_OF_THREADS, self.slurm_parameters,
                                    time_limit=self.time_limit)[0]
        job_results = job.get_job_results()['run_time_results']
        for file_dict in job_results:
            if 'dead_code_file' not in file_dict.keys():
                for loop_dict in file_dict['loops']:
                    if 'dead_code' not in loop_dict.keys():
                        key = (file_dict['file_id_by_rel_path'], loop_dict['loop_label'])
                        self.serial_run_time[key] = loop_dict['run_time']
        if not self.save_combinations_folders:
            self.__delete_combination_folder(serial_dir_path)

    def fragment_and_add_timers(self):
        main_file_path = os.path.join(self.original_files_dir, self.main_file_rel_path)
        declaration_code_to_inject_to_main_file = ""
        for index, c_file_dict in enumerate(self.make_absolute_file_list(self.original_files_dir)):
            self.__timer = Timer(c_file_dict['file_full_path'])
            self.__timer.inject_timers(index, main_file_path)
            num_of_loops = self.__timer.get_number_of_loops()
            name_of_global_array = f'____compar____arr{str(index)}'
            if num_of_loops != 0:
                self.files_loop_dict[c_file_dict['file_id_by_rel_path']] = (num_of_loops, name_of_global_array)
                declaration_code_to_inject_to_main_file += f"____compar____struct " \
                    f"{name_of_global_array}[{num_of_loops}] = {'{0}'};\n"
            else:
                self.files_loop_dict[c_file_dict['file_id_by_rel_path']] = (num_of_loops, 'no_global_var')
        self.__timer.inject_declarations_to_main_file(main_file_path, declaration_code_to_inject_to_main_file)

    def create_combination_folder(self, combination_folder_name, base_dir=None):
        if not base_dir:
            base_dir = self.combinations_dir
        combination_folder_path = os.path.join(base_dir, combination_folder_name)
        os.mkdir(combination_folder_path)
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)
        if not os.path.isdir(combination_folder_path):
            raise e.FolderError(f'Cannot create {combination_folder_path} folder')
        return combination_folder_path

    @staticmethod
    def remove_declaration_code(content):
        run_time_vars_regex = rf'double[ ]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        file_pointer_vars_regex = rf'FILE[ ]*\*[ ]*{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        struct_regex_version_1 = r'typedef struct ____compar____[^\}]*\}[^;]*;'
        struct_regex_version_2 = r'struct ____compar____[^\}]+int[^\}]+\}[^;]*;'
        struct_regex_version_3 = r'typedef struct ____compar____[^\;]*____compar____struct;'
        compar_dummy_var_regex = fr'{Timer.COMPAR_DUMMY_VAR}[^;]+;'
        content = re.sub(rf'{Timer.DECL_GLOBAL_TIMER_VAR_CODE}', '', content)
        content = re.sub(struct_regex_version_1, '', content, flags=re.DOTALL)
        content = re.sub(struct_regex_version_2, '', content, flags=re.DOTALL)
        content = re.sub(struct_regex_version_3, '', content, flags=re.DOTALL)
        content = re.sub(run_time_vars_regex, '', content, flags=re.DOTALL)
        content = re.sub(file_pointer_vars_regex, '', content, flags=re.DOTALL)
        content = re.sub(compar_dummy_var_regex, '', content, flags=re.DOTALL)
        return content

    @staticmethod
    def remove_run_time_calculation_code_code(content):
        content = re.sub(rf'{Timer.GLOBAL_TIMER_VAR_NAME}[^;]+omp_get_wtime[^;]+;', '', content)
        content = re.sub(rf'{Timer.COMPAR_VAR_PREFIX}[^;]+=[ ]*\(?[ ]*omp[^;]*;', '', content, flags=re.DOTALL)
        content = re.sub(rf'{Timer.COMPAR_VAR_PREFIX}struct[ ]+extern[^;]+;', '', content, flags=re.DOTALL)
        content = re.sub(Timer.COMPAR_VAR_PREFIX + r'struct[^\}]+arr[^\}]+\}[ ]*;', '', content, flags=re.DOTALL)
        return re.sub(rf'{Timer.COMPAR_VAR_PREFIX}arr[^;]+;', '', content, flags=re.DOTALL)

    @staticmethod
    def remove_writing_to_file_code(content):
        fopen_regex = rf'{Timer.COMPAR_VAR_PREFIX}[^;]+fopen[^;]+{re.escape(Timer.get_file_name_prefix_token())}?[^;]+;'
        fprintf_regex = rf'fprintf[^;]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        fclose_regex = rf'fclose[^;]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        main_file_at_exit_regex = r'void[ ]+____compar____atExit[^\}]+\}'
        main_file_at_exit_call_regex = r'atexit[^\;]+;'
        content = re.sub(main_file_at_exit_regex, '', content, flags=re.DOTALL)
        content = re.sub(main_file_at_exit_call_regex, '', content, flags=re.DOTALL)
        content = re.sub(fopen_regex, '', content, flags=re.DOTALL)
        content = re.sub(fprintf_regex, '', content, flags=re.DOTALL)
        content = re.sub(fclose_regex, '', content, flags=re.DOTALL)
        return content

    def remove_timer_code(self, container_folder_path):
        for c_file_dict in self.make_absolute_file_list(container_folder_path):
            try:
                with open(c_file_dict['file_full_path'], 'r') as f:
                    content = f.read()
                content = self.remove_declaration_code(content)
                content = self.remove_run_time_calculation_code_code(content)
                content = self.remove_writing_to_file_code(content)
                with open(c_file_dict['file_full_path'], 'w') as f:
                    f.write(content)
            except Exception as ex:
                raise e.FileError(f'exception in Compar.remove_timer_code: {c_file_dict["file_full_path"]}: {str(ex)}')

    def generate_summary_file(self, optimal_data, dir_path):
        file_path = os.path.join(dir_path, self.SUMMARY_FILE_NAME)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File", "Loop", "Combination", "Compiler", "Compilation Params", "Env flags",
                             "Runtime", "Speedup"])
            for curr_file in optimal_data:
                if 'dead_code_file' in curr_file.keys():
                    writer.writerow([curr_file['file_id_by_rel_path'], "" 'dead code file',
                                     "", "", "", "", ""])
                    continue
                for loop in curr_file['optimal_loops']:
                    if 'dead_code' in loop.keys():
                        writer.writerow([curr_file['file_id_by_rel_path'], loop['loop_label'], 'dead code loop',
                                         "", "", "", "", ""])
                    else:
                        combination_obj = self.__combination_json_to_obj(
                            self.db.get_combination_from_static_db(loop['_id']))
                        writer.writerow([curr_file['file_id_by_rel_path'], loop['loop_label'], loop['_id'],
                                         combination_obj.get_compiler(),
                                         combination_obj.get_parameters().get_compilation_params(),
                                         combination_obj.get_parameters().get_env_params(),
                                         loop['run_time'], loop['speedup']])

    def update_summary_file(self, best_runtime_combination, dir_path):
        file_path = os.path.join(dir_path, self.SUMMARY_FILE_NAME)
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([""])
            writer.writerow([f"Combination {best_runtime_combination.get_combination_id()}"
                             f" gave the best total runtime"])
            writer.writerow(["Compiler", "Compilation Params", "Env flags"])
            writer.writerow([best_runtime_combination.get_compiler(),
                             best_runtime_combination.get_parameters().get_compilation_params(),
                             best_runtime_combination.get_parameters().get_env_params()])
