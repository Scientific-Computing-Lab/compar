import os
import re
from time import sleep
from execute_job import ExecuteJob
from combination import Combination
from compilers.gcc import Gcc
from compilers.icc import Icc
from exceptions import UserInputError
from job_executor import JobExecutor
from file_formator import format_c_code
from job import Job
from fragmentator import Fragmentator
import shutil
import csv
from exceptions import FileError
from timer import Timer
import exceptions as e
from database import Database
from compilers.makefile import Makefile
import traceback
import logger
from combination_validator import CombinationValidator
from assets.parallelizers_mapper import parallelizers
from globals import ComparMode, ComparConfig, CombinatorConfig, LogPhrases
import copy


class Compar:
    COMPAR_COMBINATION_FOLDER_NAME = Database.COMPAR_COMBINATION_ID
    FINAL_RESULTS_FOLDER_NAME = Database.FINAL_RESULTS_COMBINATION_ID
    NUM_OF_THREADS = ComparConfig.NUM_OF_THREADS

    @staticmethod
    def set_num_of_threads(num_of_threads: int):
        Compar.NUM_OF_THREADS = num_of_threads

    @staticmethod
    def inject_c_code_to_loop(c_file_path: str, loop_id: str, c_code_to_inject: str):
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
    def __copy_folder_content(src: str, dst: str):
        for rel_path in os.listdir(src):
            src_full_path = os.path.join(src, rel_path)
            if os.path.isfile(src_full_path):
                shutil.copy(src_full_path, dst)
            elif os.path.isdir(src_full_path):
                destination_path_include_new_dir = os.path.join(dst, rel_path)
                if os.path.exists(destination_path_include_new_dir):
                    shutil.rmtree(destination_path_include_new_dir)
                shutil.copytree(src_full_path, destination_path_include_new_dir)

    @staticmethod
    def __delete_combination_folder(combination_folder_path: str):
        if os.path.exists(combination_folder_path):
            shutil.rmtree(combination_folder_path)

    @staticmethod
    def format_c_files(list_of_file_paths: list):
        for file_path in list_of_file_paths:
            format_c_code([file_path, ])

    @staticmethod
    def get_file_content(file_path: str):
        try:
            with open(file_path, 'r') as input_file:
                return input_file.read()
        except FileNotFoundError:
            raise FileError(f'File {file_path} dose not exist')

    @staticmethod
    def add_to_loop_details_about_comp_and_combination(file_path: str, start_label: str, combination_id: str,
                                                       comp_name: str):
        e.assert_file_exist(file_path)
        e.assert_file_is_empty(file_path)
        with open(file_path, 'r') as file:
            file_text = file.read()
        to_replace = ''
        to_replace += f'{start_label}\n{ComparConfig.COMBINATION_ID_C_COMMENT}{combination_id}\n'
        to_replace += f'{ComparConfig.COMPILER_NAME_C_COMMENT}{comp_name}\n'
        file_text = re.sub(f'{start_label}[ ]*\\n', to_replace, file_text)
        try:
            with open(file_path, 'w') as file:
                file.write(file_text)
        except OSError as err:
            raise e.FileError(str(err))

    @staticmethod
    def remove_optimal_combinations_details(file_paths_list: list):
        regex_pattern = r'\n.+COMBINATION_ID[^\n]+\n+[^\n]+?\n*.+COMPILER_NAME[^\n]+'
        for file_path in file_paths_list:
            with open(file_path, 'r+') as fp:
                file_content = fp.read()
                file_content = re.sub(regex_pattern, '', file_content)
                fp.seek(0)
                fp.write(file_content)
                fp.truncate()

    @staticmethod
    def replace_loops_in_files(origin_path: str, destination_path: str, start_label: str, end_label: str):

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
    def update_summary_file(dir_path: str, best_runtime_combination_id: str, total_rum_time: float,
                            best_combination=None):
        file_path = os.path.join(dir_path, ComparConfig.SUMMARY_FILE_NAME)
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([""])
            writer.writerow([f"{best_runtime_combination_id}"
                             f" combination gave the best total runtime"])
            writer.writerow([""])
            if best_combination:
                writer.writerow(["Compiler", "Compilation Flags", "OMP RTL Parameters", "OMP Directive Parameters"])
                writer.writerow([best_combination.get_compiler(),
                                 best_combination.get_parameters().get_compilation_params(),
                                 best_combination.get_parameters().get_omp_rtl_params(),
                                 best_combination.get_parameters().get_omp_directives_params()])
                writer.writerow([""])
            writer.writerow(['Total run time:', str(total_rum_time)])

    def __init__(self,
                 input_dir: str,
                 output_dir: str,
                 project_name: str,
                 main_file_rel_path: str,
                 binary_compiler_type: str = "",
                 binary_compiler_version: str = None,
                 binary_compiler_flags: list = None,
                 save_combinations_folders: bool = False,
                 is_make_file: bool = False,
                 makefile_commands: list = None,
                 makefile_exe_folder_rel_path: str = "",
                 makefile_output_exe_file_name: str = "",
                 ignored_rel_paths: list = None,
                 include_dirs_list: list = None,
                 main_file_parameters: list = None,
                 slurm_parameters: list = None,
                 extra_files: list = None,
                 time_limit: str = None,
                 slurm_partition=ComparConfig.DEFAULT_SLURM_PARTITION,
                 test_file_path: str = '',
                 mode=ComparConfig.MODES[ComparConfig.DEFAULT_MODE],
                 code_with_markers: bool = False,
                 clear_db: bool = False,
                 multiple_combinations: int = 1,
                 log_level: int = logger.DEFAULT_LOG_LEVEL):

        self.db = Database(project_name, mode)

        working_directory = os.path.join(output_dir, self.db.get_project_name())
        if mode == ComparMode.CONTINUE:
            e.assert_original_files_folder_exists(working_directory)
        else:
            if os.path.exists(working_directory):
                shutil.rmtree(working_directory)
        os.makedirs(working_directory, exist_ok=True)

        logger.initialize(log_level, working_directory)
        logger.info('Starting ComPar execution')

        e.assert_rel_path_starts_without_sep(makefile_exe_folder_rel_path)
        e.assert_rel_path_starts_without_sep(main_file_rel_path)
        if slurm_parameters and len(slurm_parameters) == 1:
            slurm_parameters = str(slurm_parameters[0]).split(' ')
        e.assert_folder_exist(input_dir)
        e.assert_user_json_structure()

        if not is_make_file:
            e.assert_only_files(input_dir)
        if not include_dirs_list:
            include_dirs_list = []
        if not makefile_commands:
            makefile_commands = []
        if not binary_compiler_flags:
            binary_compiler_flags = []
        if not main_file_parameters:
            main_file_parameters = []
        if not slurm_parameters:
            slurm_parameters = ComparConfig.DEFAULT_SLURM_PARAMETERS
        if not ignored_rel_paths:
            ignored_rel_paths = []
        if not test_file_path:
            test_file_path = CombinationValidator.UNIT_TEST_DEFAULT_PATH
        if not extra_files:
            extra_files = []

        self.binary_compiler = None
        self.__timer = None
        self.serial_run_time = {}
        self.files_loop_dict = {}
        self.main_file_rel_path = main_file_rel_path
        self.save_combinations_folders = save_combinations_folders
        self.binary_compiler_version = binary_compiler_version
        self.ignored_rel_paths = ignored_rel_paths
        self.include_dirs_list = include_dirs_list
        self.time_limit = time_limit
        self.slurm_partition = slurm_partition
        self.parallel_jobs_pool_executor = JobExecutor(Compar.NUM_OF_THREADS)
        self.mode = mode
        self.code_with_markers = code_with_markers
        self.clear_db = clear_db
        self.multiple_combinations = multiple_combinations

        # Unit test
        self.test_file_path = test_file_path
        e.assert_file_exist(self.test_file_path)
        e.assert_test_file_name(os.path.basename(self.test_file_path))
        e.assert_test_file_function_name(self.test_file_path)

        # Initiate Compar environment
        e.assert_forbidden_characters(working_directory)
        self.working_directory = working_directory
        self.backup_files_dir = os.path.join(working_directory, ComparConfig.BACKUP_FOLDER_NAME)
        self.original_files_dir = os.path.join(working_directory, ComparConfig.ORIGINAL_FILES_FOLDER_NAME)
        if self.mode == ComparMode.CONTINUE:
            e.assert_folder_exist(self.original_files_dir)
            self.__delete_combination_folder(os.path.join(working_directory, self.COMPAR_COMBINATION_FOLDER_NAME))
            self.__delete_combination_folder(os.path.join(working_directory, self.FINAL_RESULTS_FOLDER_NAME))

        self.combinations_dir = os.path.join(working_directory, ComparConfig.COMBINATIONS_FOLDER_NAME)
        self.__create_directories_structure(input_dir)

        # Compilers variables
        self.relative_c_file_list = self.make_relative_c_file_list(self.original_files_dir)
        if self.code_with_markers:
            file_paths = [file['file_full_path'] for file in self.make_absolute_file_list(self.original_files_dir)]
            self.remove_optimal_combinations_details(file_paths)
        self.binary_compiler_type = binary_compiler_type
        self.parallelizers = dict()
        for name, ctor in parallelizers.items():
            self.parallelizers[name] = ctor("", include_dirs_list=self.include_dirs_list, extra_files=extra_files)

        # Compiler flags
        self.user_binary_compiler_flags = binary_compiler_flags

        # Makefile
        self.is_make_file = is_make_file
        self.makefile_commands = makefile_commands
        self.makefile_exe_folder_rel_path = makefile_exe_folder_rel_path
        self.makefile_output_exe_file_name = makefile_output_exe_file_name

        # Main file
        self.main_file_parameters = main_file_parameters

        # SLURM
        self.slurm_parameters = slurm_parameters

        # Initialization
        if not is_make_file:
            self.__initialize_binary_compiler()

        self.db.create_collections()

    def clear_related_collections(self):
        if self.db:
            self.db.delete_all_related_collections()

    def inject_rtl_params_to_loop(self, file_dict: dict, omp_rtl_params: list):
        if not omp_rtl_params:
            return
        c_file_path = file_dict['file_full_path']
        e.assert_file_exist(c_file_path)
        with open(c_file_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        for loop_id in range(1, self.files_loop_dict[file_dict['file_id_by_rel_path']][0] + 1):
            start_loop_marker = f'{Fragmentator.get_start_label()}{loop_id}'
            end_loop_marker = f'{Fragmentator.get_end_label()}{loop_id}'
            start_marker_pattern = rf'{start_loop_marker}[ \t]*\n'
            loop_pattern = rf'{start_marker_pattern}.*{end_loop_marker}[ \t]*\n'
            loop_before_changes = re.search(loop_pattern, c_code, re.DOTALL).group()
            loop_prefix_pattern = rf'{start_marker_pattern}.*?(?=[\t ]*for[ \t]*\()'
            loop_prefix = re.search(loop_prefix_pattern, loop_before_changes, re.DOTALL).group()
            loop_body_and_suffix = re.sub(re.escape(loop_prefix), '', loop_before_changes)
            params_code = f'{start_loop_marker}\n'
            for param in omp_rtl_params:
                omp_function_name = re.search(r'.+(?=\(.*\))', param).group()
                if omp_function_name in loop_prefix:
                    loop_prefix = re.sub(rf'{omp_function_name}[^;]*;[^\n]*\n', '', loop_prefix, re.DOTALL)
                params_code += f'{param}\n'
            loop_prefix = re.sub(rf'{start_marker_pattern}', params_code, loop_prefix)
            new_loop = f'{loop_prefix}{loop_body_and_suffix}'
            c_code = c_code.replace(loop_before_changes, new_loop)
        try:
            with open(c_file_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))

    def inject_directive_params_to_loop(self, file_dict: dict, omp_directive_params: list):
        if not omp_directive_params:
            return
        c_file_path = file_dict['file_full_path']
        e.assert_file_exist(c_file_path)
        format_c_code([c_file_path, ])  # mainly to arrange directives in a single line
        with open(c_file_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        for loop_id in range(1, self.files_loop_dict[file_dict['file_id_by_rel_path']][0] + 1):
            start_loop_marker = f'{Fragmentator.get_start_label()}{loop_id}'
            end_loop_marker = f'{Fragmentator.get_end_label()}{loop_id}'
            start_marker_pattern = rf'{start_loop_marker}[ \t]*\n'
            loop_pattern = rf'{start_marker_pattern}.*{end_loop_marker}[ \t]*\n'
            loop_before_changes = re.search(loop_pattern, c_code, re.DOTALL).group()
            loop_prefix_pattern = rf'{start_marker_pattern}.*?(?=[\t ]*for[ \t]*\()'
            loop_prefix = re.search(loop_prefix_pattern, loop_before_changes, re.DOTALL).group()
            loop_body_and_suffix = re.sub(re.escape(loop_prefix), '', loop_before_changes)
            pragma_pattern = r'#pragma omp[^\n]+\n'
            pragma = re.search(rf'{pragma_pattern}', loop_prefix)
            if pragma:
                pragma = pragma.group().replace('\n', '')
                new_directives = ''
                for directive in omp_directive_params:
                    pragma_type, directive = directive.split('_', 1)
                    pragma_name = re.search(r'[^(]+', directive).group()
                    if not re.search(rf' {pragma_type} ?', pragma):
                        if pragma_type == CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX:
                            pragma = re.sub(r'pragma omp', f'pragma omp {pragma_type}', pragma)
                        if pragma_type == CombinatorConfig.FOR_DIRECTIVE_PREFIX:
                            if re.search(rf' {CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX} ?', pragma):
                                new_text = f'pragma omp {CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX} {pragma_type} '
                                pragma = re.sub(rf'pragma omp {CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX} ?',
                                                new_text,
                                                pragma)
                            else:
                                pragma = re.sub(r'pragma omp', f'pragma omp {pragma_type}', pragma)
                    if pragma_name in pragma:
                        pragma = re.sub(rf'{"pragma_name"}(?:\([^)]+\))? ?', '', pragma)
                    new_directives += f' {directive}'
                new_pragma = f'{pragma} {new_directives}\n'
                new_prefix = re.sub(rf'{pragma_pattern}', new_pragma, loop_prefix)
                c_code = c_code.replace(loop_before_changes, f'{new_prefix}{loop_body_and_suffix}')
        try:
            with open(c_file_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))

    def generate_optimal_code(self):
        logger.info('Start to combine the Compar combination')
        optimal_loops_data = []

        # copy final results into this folder
        compar_combination_folder_path = self.create_combination_folder(self.COMPAR_COMBINATION_FOLDER_NAME,
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
                    current_file["optimal_loops"].append({'_id': Database.SERIAL_COMBINATION_ID,
                                                          'loop_label': str(loop_id), 'dead_code': True})
                    current_optimal_id = Database.SERIAL_COMBINATION_ID

                # if the optimal combination is the serial => do nothing
                if current_optimal_id != Database.SERIAL_COMBINATION_ID:
                    current_optimal_combination = Combination.json_to_obj(
                        self.db.get_combination_from_static_db(current_optimal_id))
                    current_combination_folder_path = self.create_combination_folder(
                        ComparConfig.OPTIMAL_CURRENT_COMBINATION_FOLDER_NAME, base_dir=self.working_directory)
                    files_list = self.make_absolute_file_list(current_combination_folder_path)
                    current_comp_name = current_optimal_combination.compiler_name

                    # get direct file path to inject params
                    src_file_path = list(filter(lambda x: x['file_id_by_rel_path'] == file_id_by_rel_path, files_list))
                    src_file_path = src_file_path[0]['file_full_path']

                    # parallelize and inject
                    self.parallel_compilation_of_one_combination(current_optimal_combination,
                                                                 current_combination_folder_path)

                    # replace loop in c file using final_files_list
                    target_file_path = list(filter(lambda x: x['file_id_by_rel_path'] == file_id_by_rel_path,
                                                   final_files_list))
                    target_file_path = target_file_path[0]['file_full_path']

                    Compar.replace_loops_in_files(src_file_path, target_file_path, start_label, end_label)
                    Compar.add_to_loop_details_about_comp_and_combination(target_file_path, start_label,
                                                                          current_optimal_id, current_comp_name)
                    sleep(1)  # prevent IO error
                    shutil.rmtree(current_combination_folder_path)
            optimal_loops_data.append(current_file)

        # remove timers code
        Timer.remove_timer_code(self.make_absolute_file_list(compar_combination_folder_path))
        # inject new code
        Timer.inject_timer_to_compar_mixed_file(os.path.join(compar_combination_folder_path,
                                                             self.main_file_rel_path), compar_combination_folder_path)
        self.generate_summary_file(optimal_loops_data, compar_combination_folder_path)
        try:
            logger.info('Compiling Compar combination')
            self.compile_combination_to_binary(compar_combination_folder_path, inject=False)
            job = Job(compar_combination_folder_path, Combination(Database.COMPAR_COMBINATION_ID,
                                                                  ComparConfig.MIXED_COMPILER_NAME, None), [])
            logger.info('Running Compar combination')
            self.execute_job(job, self.serial_run_time)
        except Exception as ex:
            msg = f'Exception in Compar: {ex}\ngenerate_optimal_code: cannot compile compar combination'
            self.save_combination_as_failure(Database.COMPAR_COMBINATION_ID, msg, compar_combination_folder_path)
        logger.info(LogPhrases.NEW_COMBINATION.format(Database.FINAL_RESULTS_COMBINATION_ID))
        # Check for best total runtime
        best_runtime_combination_id = self.db.get_total_runtime_best_combination()
        best_combination_obj = None
        if best_runtime_combination_id != Database.COMPAR_COMBINATION_ID:
            logger.info(f'Combination #{best_runtime_combination_id} is more optimal than Compar combination')
            best_combination_obj = Combination.json_to_obj(
                self.db.get_combination_from_static_db(best_runtime_combination_id))
            final_results_folder_path = self.create_combination_folder(
                self.FINAL_RESULTS_FOLDER_NAME, self.working_directory)
            try:
                if best_runtime_combination_id != Database.SERIAL_COMBINATION_ID:
                    self.parallel_compilation_of_one_combination(best_combination_obj, final_results_folder_path)
                self.compile_combination_to_binary(final_results_folder_path)
                summary_file_path = os.path.join(compar_combination_folder_path, ComparConfig.SUMMARY_FILE_NAME)
                summary_file_new_path = os.path.join(final_results_folder_path, ComparConfig.SUMMARY_FILE_NAME)
                shutil.move(summary_file_path, summary_file_new_path)
            except Exception as ex:
                raise Exception(f"Total runtime calculation - The optimal file could not be compiled, combination"
                                f" {best_runtime_combination_id}.\n{ex}")
        else:
            logger.info(f'Compar combination is the optimal combination')
            final_folder_path = os.path.join(self.working_directory, self.FINAL_RESULTS_FOLDER_NAME)
            if os.path.exists(final_folder_path):
                shutil.rmtree(final_folder_path)
            shutil.copytree(compar_combination_folder_path, final_folder_path)
        # remove compar code from all the files in final result folder
        final_folder_path = os.path.join(self.working_directory, self.FINAL_RESULTS_FOLDER_NAME)
        Timer.remove_timer_code(self.make_absolute_file_list(final_folder_path))
        final_combination_results = self.db.get_combination_results(best_runtime_combination_id)
        if final_combination_results:
            final_combination_results['_id'] = Database.FINAL_RESULTS_COMBINATION_ID
            final_combination_results['from_combination'] = best_runtime_combination_id
            self.db.insert_new_combination_results(final_combination_results)
            with open(os.path.join(final_folder_path, Timer.TOTAL_RUNTIME_FILENAME), 'w') as f:
                f.write(str(final_combination_results['total_run_time']))
            self.update_summary_file(final_folder_path, best_runtime_combination_id,
                                     final_combination_results['total_run_time'], best_combination_obj)
        # format all optimal files
        self.format_c_files([file_dict['file_full_path'] for file_dict in
                             self.make_absolute_file_list(final_folder_path)])
        self.db.remove_unused_data(Database.COMPAR_COMBINATION_ID)
        self.db.remove_unused_data(Database.FINAL_RESULTS_COMBINATION_ID)
        final_result_speedup, final_result_runtime = self.db.get_final_result_speedup_and_runtime()
        logger.info(LogPhrases.FINAL_RESULTS_SUMMARY.format(final_result_speedup, final_result_runtime))
        if self.clear_db:
            self.clear_related_collections()
        self.db.close_connection()

    def __get_parallel_compiler_by_name(self, compiler_name: str):
        return self.parallelizers[compiler_name.lower()]

    def __replace_result_file_name_prefix(self, container_folder_path: str):
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
            Icc.NAME: Icc(version=self.binary_compiler_version),
            Gcc.NAME: Gcc(version=self.binary_compiler_version)
        }
        self.binary_compiler = binary_compilers_map[self.binary_compiler_type.lower()]

    def parallel_compilation_of_one_combination(self, combination_obj: Combination, combination_folder_path: str):
        compiler_name = combination_obj.get_compiler()
        parallel_compiler = self.__get_parallel_compiler_by_name(compiler_name)
        parallel_compiler.initiate_for_new_task(combination_obj.get_parameters().get_compilation_params(),
                                                combination_folder_path,
                                                self.make_absolute_file_list(combination_folder_path))
        pre_processing_args = dict()
        parallel_compiler.pre_processing(**pre_processing_args)
        parallel_compiler.compile()
        post_processing_args = {'files_loop_dict': self.files_loop_dict}
        parallel_compiler.post_processing(**post_processing_args)
        omp_rtl_params = combination_obj.get_parameters().get_omp_rtl_params()
        omp_directive_params = combination_obj.get_parameters().get_omp_directives_params()
        for file_dict in self.make_absolute_file_list(combination_folder_path):
            self.inject_rtl_params_to_loop(file_dict, omp_rtl_params)
            self.inject_directive_params_to_loop(file_dict, omp_directive_params)

    def compile_combination_to_binary(self, combination_folder_path: str, extra_flags_list: list = None, inject=True):
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

    def execute_job(self, job: Job, serial_run_time: dict = None):
        execute_job_obj = ExecuteJob(job, self.files_loop_dict, self.db, self.parallel_jobs_pool_executor.get_db_lock(),
                                     serial_run_time, self.relative_c_file_list, self.slurm_partition,
                                     self.test_file_path, self.time_limit)
        execute_job_obj.run(self.slurm_parameters)
        return job

    def run_and_save_job(self, job_obj: Job):
        try:
            job_obj = self.execute_job(job_obj, self.serial_run_time)
        except Exception as ex:
            logger.info_error(f'Exception at {Compar.__name__}: {ex}')
            logger.debug_error(f'{traceback.format_exc()}')
        finally:
            if not self.save_combinations_folders:
                self.__delete_combination_folder(job_obj.get_directory_path())

    def save_combination_as_failure(self, combination_id: str, error_msg: str, combination_folder_path: str):
        combination_dict = {
            '_id': combination_id,
            'error': error_msg
        }
        self.db.insert_new_combination_results(combination_dict)
        sleep(1)
        if not self.save_combinations_folders:
            self.__delete_combination_folder(combination_folder_path)

    def run_parallel_combinations(self):
        logger.info('Start to work on parallel combinations')
        self.parallel_jobs_pool_executor.create_jobs_pool()
        # if equal to one - we don't need to concatenate the number of repetitions to combination id nor calculate avg
        is_multiple_combinations = self.multiple_combinations > 1
        for combination_json in self.db.combinations_iterator():
            original_combination_obj = Combination.json_to_obj(combination_json)
            logger.info(LogPhrases.NEW_COMBINATION.format(original_combination_obj.combination_id))
            for i in range(self.multiple_combinations):
                if is_multiple_combinations:
                    combination_obj = copy.deepcopy(original_combination_obj)
                    combination_obj.combination_id = f'{combination_obj.combination_id}_{i}'
                    logger.info(f'#{i} repetition of {original_combination_obj.combination_id} combination')
                else:
                    combination_obj = original_combination_obj
                combination_folder_path = self.create_combination_folder(str(combination_obj.get_combination_id()))
                try:
                    self.parallel_compilation_of_one_combination(combination_obj, combination_folder_path)
                    self.compile_combination_to_binary(combination_folder_path)
                except Exception as ex:
                    logger.info_error(f'Exception at {Compar.__name__}: {ex}')
                    logger.debug_error(f'{traceback.format_exc()}')
                    self.save_combination_as_failure(combination_obj.get_combination_id(), str(ex),
                                                     combination_folder_path)
                    continue
                job = Job(combination_folder_path, combination_obj, self.main_file_parameters)
                self.parallel_jobs_pool_executor.run_job_in_thread(self.run_and_save_job, job)
        self.parallel_jobs_pool_executor.wait_and_finish_pool()
        if is_multiple_combinations:
            self.calculate_multiple_combinations_average()
        logger.info('Finish to work on all the parallel combinations')

    def calculate_multiple_combinations_average(self):
        for combination_json in self.db.combinations_iterator():
            total_results = dict()
            combination_id = Combination.json_to_obj(combination_json).combination_id
            logger.info(f'Calculating average of {combination_id} combination')
            for i in range(self.multiple_combinations):
                current_id = f'{combination_id}_{i}'
                current_results = self.db.get_combination_results(current_id)
                if 'error' in current_results.keys():
                    current_results['error'] = f"from {current_id}: {current_results['error']}"
                if not total_results:
                    total_results = current_results
                else:
                    if 'error' in current_results.keys():
                        total_results['error'] = f"{total_results.get('error', '')}\n{current_results['error']}"
                    elif 'error' not in total_results.keys():
                        total_results['total_run_time'] += current_results['total_run_time']
                        for j, file in enumerate(current_results['run_time_results']):
                            if 'dead_code_file' in file.keys():
                                total_results['run_time_results'][j] = file
                            elif 'dead_code_file' not in total_results['run_time_results'][j].keys():
                                for k, loop in enumerate(file['loops']):
                                    if 'dead_code' in loop.keys():
                                        total_results['run_time_results'][j]['loops'][k] = loop
                                    elif 'dead_code' not in total_results['run_time_results'][j]['loops'][k].keys():
                                        total_results['run_time_results'][j]['loops'][k]['run_time'] += loop['run_time']
                self.db.delete_combination(current_id)
            if 'error' not in total_results.keys():
                try:
                    total_results['total_run_time'] /= self.multiple_combinations
                except KeyError as ex:
                    total_results['error'] = str(ex)
                for file in total_results['run_time_results']:
                    if 'dead_code_file' not in file.keys():
                        for loop in file['loops']:
                            if 'dead_code' not in loop.keys():
                                loop['run_time'] /= self.multiple_combinations
                                key = (file['file_id_by_rel_path'], loop['loop_label'])
                                try:
                                    loop['speedup'] = self.serial_run_time[key] / loop['run_time']
                                except ZeroDivisionError:
                                    loop['speedup'] = float('inf')
                                except Exception as ex:  # if serial loop is dead_code and parallel is not, KeyError
                                    total_results['error'] = str(ex)
            total_results['_id'] = combination_id
            self.db.insert_new_combination_results(total_results)

    def __create_directories_structure(self, input_dir: str):
        logger.info('Creating Compar directories structure')
        if self.mode != ComparMode.CONTINUE:
            os.makedirs(self.original_files_dir, exist_ok=True)
        os.makedirs(self.combinations_dir, exist_ok=True)
        os.makedirs(self.backup_files_dir, exist_ok=True)

        if os.path.isdir(input_dir):
            if self.mode != ComparMode.CONTINUE:
                self.__copy_folder_content(input_dir, self.original_files_dir)
                self.__copy_folder_content(input_dir, self.backup_files_dir)
        else:
            raise UserInputError('The input path must be directory')

    def __copy_sources_to_combination_folder(self, combination_folder_path: str):
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)

    def make_relative_c_file_list(self, base_dir: str):
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

    def make_absolute_file_list(self, base_dir_path: str):
        return list(map(lambda file_dict: {'file_name': file_dict['file_name'],
                                           'file_full_path': os.path.join(base_dir_path,
                                                                          file_dict['file_relative_path']),
                                           'file_id_by_rel_path': file_dict['file_relative_path']
                                           }, self.relative_c_file_list))

    def __run_binary_compiler(self, serial_dir_path: str):
        self.binary_compiler.initiate_for_new_task(compilation_flags=self.user_binary_compiler_flags,
                                                   input_file_directory=serial_dir_path,
                                                   main_c_file=self.main_file_rel_path)
        self.binary_compiler.compile()

    def run_serial(self):
        logger.info(LogPhrases.NEW_COMBINATION.format(Database.SERIAL_COMBINATION_ID))
        serial_dir_path = os.path.join(self.combinations_dir, Database.SERIAL_COMBINATION_ID)
        if self.mode == ComparMode.CONTINUE and self.db.combination_has_results(Database.SERIAL_COMBINATION_ID):
            job_results = self.db.get_combination_results(Database.SERIAL_COMBINATION_ID)['run_time_results']
        else:
            shutil.rmtree(serial_dir_path, ignore_errors=True)
            os.mkdir(serial_dir_path)
            self.__copy_sources_to_combination_folder(serial_dir_path)
            Timer.inject_atexit_code_to_main_file(os.path.join(serial_dir_path, self.main_file_rel_path),
                                                  self.files_loop_dict, serial_dir_path)

            if self.is_make_file:
                compiler_type = Makefile.NAME
                makefile = Makefile(serial_dir_path, self.makefile_exe_folder_rel_path,
                                    self.makefile_output_exe_file_name, self.makefile_commands)
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
            job = self.execute_job(job)
            job_results = job.get_job_results()['run_time_results']
        for file_dict in job_results:
            if 'dead_code_file' not in file_dict.keys():
                for loop_dict in file_dict['loops']:
                    if 'dead_code' not in loop_dict.keys():
                        key = (file_dict['file_id_by_rel_path'], loop_dict['loop_label'])
                        self.serial_run_time[key] = loop_dict['run_time']
        if not self.save_combinations_folders:
            self.__delete_combination_folder(serial_dir_path)
        logger.info('Finish to work on serial combination')

    def fragment_and_add_timers(self):
        logger.info('Start to enumerating loops and injecting run time timers')
        main_file_path = os.path.join(self.original_files_dir, self.main_file_rel_path)
        declaration_code_to_inject_to_main_file = ""
        for index, c_file_dict in enumerate(self.make_absolute_file_list(self.original_files_dir)):
            if self.mode == ComparMode.CONTINUE:
                num_of_loops = Fragmentator.count_loops_in_prepared_file(c_file_dict['file_full_path'])
            else:
                self.__timer = Timer(c_file_dict['file_full_path'], code_with_markers=self.code_with_markers)
                self.__timer.inject_timers(index, main_file_path)
                num_of_loops = self.__timer.get_number_of_loops()
            name_of_global_array = f'{Timer.NAME_OF_GLOBAL_ARRAY}{str(index)}'
            if num_of_loops != 0:
                self.files_loop_dict[c_file_dict['file_id_by_rel_path']] = (num_of_loops, name_of_global_array)
                declaration_code_to_inject_to_main_file += Timer.DECL_GLOBAL_ARRAY.format(
                    name_of_global_array, num_of_loops)
            else:
                self.files_loop_dict[c_file_dict['file_id_by_rel_path']] = (num_of_loops, 'no_global_var')
        if self.mode != ComparMode.CONTINUE:
            self.__timer.inject_declarations_to_main_file(main_file_path, declaration_code_to_inject_to_main_file)
        logger.info('Finish to enumerating loops and injecting run time timers')

    def create_combination_folder(self, combination_folder_name: str, base_dir: str = None):
        if not base_dir:
            base_dir = self.combinations_dir
        combination_folder_path = os.path.join(base_dir, combination_folder_name)
        if os.path.exists(combination_folder_path):
            shutil.rmtree(combination_folder_path)
        os.mkdir(combination_folder_path)
        self.__copy_folder_content(self.original_files_dir, combination_folder_path)
        if not os.path.isdir(combination_folder_path):
            raise e.FolderError(f'Cannot create {combination_folder_path} folder')
        return combination_folder_path

    def generate_summary_file(self, optimal_data: list, dir_path: str):
        file_path = os.path.join(dir_path, ComparConfig.SUMMARY_FILE_NAME)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File", "Loop", "Combination", "Compiler", "Compilation Flags", "OMP RTL Parameters",
                             "OMP Directive Parameters", "Runtime", "Speedup"])
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
                        combination_obj = Combination.json_to_obj(
                            self.db.get_combination_from_static_db(loop['_id']))
                        writer.writerow([curr_file['file_id_by_rel_path'], loop['loop_label'], loop['_id'],
                                         combination_obj.get_compiler(),
                                         combination_obj.get_parameters().get_compilation_params(),
                                         combination_obj.get_parameters().get_omp_rtl_params(),
                                         combination_obj.get_parameters().get_omp_directives_params(),
                                         loop['run_time'], loop['speedup']])
