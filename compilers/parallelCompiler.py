from abc import ABC
from compilers.compiler import Compiler
from exceptions import CompilationError
from subprocess_handler import run_subprocess
import subprocess
import logger
import json
import os


class ParallelCompiler(Compiler, ABC):
    NAME = ''

    def __init__(self, version, input_file_directory=None, compilation_flags=None, file_list=None,
                 include_dirs_list=None):
        super().__init__(version, input_file_directory, compilation_flags)
        self._file_list = file_list
        self.include_dirs_list = include_dirs_list

    def initiate_for_new_task(self, compilation_flags, input_file_directory, file_list):
        super().initiate_for_new_task(compilation_flags, input_file_directory)
        self.set_file_list(file_list)

    def set_file_list(self, file_list):
        self._file_list = file_list

    def get_file_list(self):
        return self._file_list

    def compile(self):
        if not self.get_file_list():
            raise CompilationError("Missing file_list to compile!")
        if not self.get_input_file_directory():
            raise CompilationError("Missing working directory!")

    def __run_user_script(self, script_name):
        json_script_file_path = os.path.join('assets', script_name)
        if os.path.exists(json_script_file_path):
            with open(json_script_file_path, 'r') as f:
                json_content = json.load(f)
            if self.NAME in json_content:
                user_script_path = json_content[self.NAME]
                if os.path.exists(user_script_path):
                    try:
                        std_out, std_err, ret_code = run_subprocess(user_script_path)
                        logger.debug(std_out)
                        logger.debug_error(std_err)
                    except subprocess.CalledProcessError as e:
                        logger.info_error(f'{self.NAME}: user {script_name} script return with {e.returncode}: {e}')
                        logger.info(e.output)
                        logger.info_error(e.stderr)

    def pre_processing(self, **kwargs):
        self.__run_user_script('pre_processing.json')

    def post_processing(self, **kwargs):
        self.__run_user_script('post_processing.json')
