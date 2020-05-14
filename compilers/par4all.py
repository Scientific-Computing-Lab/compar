from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, FileError, CombinationFailure
import subprocess
import os
import re
from subprocess_handler import run_subprocess
import logger
import traceback
import shutil
from globals import Par4allConfig, GlobalsConfig


class Par4all(ParallelCompiler):
    NAME = 'par4all'

    def __init__(self, version: str, compilation_flags: list = None, input_file_directory: str = None,
                 file_list: list = None, include_dirs_list: list = None, extra_files: list = None, **kwargs):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list, **kwargs)
        self.extra_files = [] if not extra_files else extra_files
        self.files_to_compile = []

    def __copy_pips_stubs_to_folder(self):
        destination_folder_path = self.get_input_file_directory()
        pips_stubs_path = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, Par4allConfig.PIPS_STUBS_NAME)
        if Par4allConfig.PIPS_STUBS_NAME not in os.listdir(destination_folder_path):
            shutil.copy(pips_stubs_path, destination_folder_path)
        return os.path.join(destination_folder_path, Par4allConfig.PIPS_STUBS_NAME)

    @staticmethod
    def remove_code_from_file(file_path: str, code_to_be_removed: str):
        try:
            with open(file_path, 'r+') as f:
                file_content = f.read()
                file_content = file_content.replace(code_to_be_removed, '')
                f.seek(0)
                f.write(file_content)
                f.truncate()
        except Exception as e:
            raise FileError(str(e))

    @staticmethod
    def inject_code_at_the_top(file_path: str, code_to_be_injected: str):
        try:
            with open(file_path, 'r+') as f:
                file_content = f.read()
                file_content = code_to_be_injected + '\n' + file_content
                f.seek(0)
                f.write(file_content)
                f.truncate()
        except Exception as e:
            raise FileError(str(e))

    @staticmethod
    def __remove_bswap_function(file_path: str):
        bswap_regex = re.compile(r'static __uint64_t __bswap_64[^\}]*\}', flags=re.DOTALL)
        try:
            with open(file_path, 'r+') as f:
                content = f.read()
                if bswap_regex.match(content):
                    content = bswap_regex.sub('', content)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
        except Exception as e:
            logger.info_error(f'Exception at {Par4all.__name__}: {e}')
            logger.debug_error(f'{traceback.format_exc()}')

    def initiate_for_new_task(self, compilation_flags: list, input_file_directory: str, file_list: list):
        super().initiate_for_new_task(compilation_flags, input_file_directory, file_list)
        self.files_to_compile = []

    def __run_p4a_process(self):
        self.files_to_compile += [file_dict['file_full_path'] for file_dict in self.get_file_list()]
        command = 'PATH=/bin:$PATH p4a -vv ' + ' '.join(self.files_to_compile)
        if self.extra_files:
            command += f' {" ".join(self.extra_files)}'
        command += ' ' + ' '.join(map(str, super().get_compilation_flags()))
        if self.include_dirs_list:
            command += ' -I ' + ' -I '.join(map(lambda x: os.path.join(self.get_input_file_directory(), str(x)),
                                                self.include_dirs_list))
        try:
            logger.info(f'{Par4all.__name__}: start parallelizing')
            stdout, stderr, ret_code = run_subprocess([command, ], self.get_input_file_directory())
            log_file_path = os.path.join(self.get_input_file_directory(), Par4allConfig.LOG_FILE_NAME)
            logger.log_to_file(f'{stdout}\n{stderr}', log_file_path)
            logger.debug(f'{Par4all.__name__}: {stdout}')
            logger.debug_error(f'{Par4all.__name__}: {stderr}')
            logger.info(f'{Par4all.__name__}: finished parallelizing')
        except subprocess.CalledProcessError as e:
            log_file_path = os.path.join(self.get_input_file_directory(), Par4allConfig.LOG_FILE_NAME)
            logger.log_to_file(f'{e.output}\n{e.stderr}', log_file_path)
            raise CombinationFailure(f'par4all return with {e.returncode} code: {str(e)} : {e.output} : {e.stderr}')
        except Exception as e:
            raise CompilationError(f"{e}\nfiles in directory {self.get_input_file_directory()} failed to be parallel!")

    def compile(self):
        try:
            super().compile()
            self.__run_p4a_process()
            for root, dirs, files in os.walk(self.get_input_file_directory()):
                for file in files:
                    full_path = os.path.join(root, file)
                    if file.endswith(Par4allConfig.PARALLEL_FILE_EXTENSION):
                        os.rename(full_path, full_path[0:-6] + '.c')
                        full_path = full_path[0:-6] + '.c'
                        self.__remove_bswap_function(full_path)
                        with open(full_path, "r+") as f:
                            input_file_text = f.read()
                            if GlobalsConfig.OMP_HEADER not in input_file_text:
                                input_file_text = f'{GlobalsConfig.IFDEF_OMP_HEADER}\n{input_file_text}'
                                f.seek(0)
                                f.write(input_file_text)
                                f.truncate()
        except Exception as e:
            raise CompilationError(f"{e}\nFiles in directory {self.get_input_file_directory()} failed to be parallel!")

    def pre_processing(self, **kwargs):
        super().pre_processing(**kwargs)
        pips_file_path = self.__copy_pips_stubs_to_folder()
        self.files_to_compile.append(pips_file_path)

    def post_processing(self, **kwargs):
        super().post_processing(**kwargs)
        os.remove(os.path.join(self.get_input_file_directory(), Par4allConfig.PIPS_STUBS_NAME))
