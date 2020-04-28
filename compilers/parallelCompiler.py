from abc import ABC
from compilers.compiler import Compiler
from exceptions import CompilationError
from subprocess_handler import run_subprocess
import subprocess
import logger
import json
import os
from globals import GlobalsConfig, ParallelCompilerConfig


class ParallelCompiler(Compiler, ABC):
    NAME = ''

    def __init__(self, version: str, compilation_flags: list = None, input_file_directory: str = None,
                 file_list: list = None, include_dirs_list: list = None, **kwargs):
        super().__init__(version, compilation_flags, input_file_directory)
        self._file_list = file_list
        self.include_dirs_list = include_dirs_list

    def initiate_for_new_task(self, compilation_flags: list, input_file_directory: str, file_list: list):
        super().initiate_for_new_task(compilation_flags, input_file_directory)
        self.set_file_list(file_list)

    def set_file_list(self, file_list: list):
        self._file_list = file_list

    def get_file_list(self):
        return self._file_list

    def compile(self):
        if not self.get_file_list():
            raise CompilationError("Missing file_list to compile!")
        if not self.get_input_file_directory():
            raise CompilationError("Missing working directory!")

    def __run_user_script(self, script_name: str):
        json_script_file_path = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, script_name)
        if os.path.exists(json_script_file_path):
            with open(json_script_file_path, 'r') as f:
                json_content = json.load(f)
            if self.NAME in json_content:
                user_script_path = json_content[self.NAME]
                if os.path.exists(user_script_path):
                    try:
                        script_command = f'{user_script_path} {self.get_input_file_directory()}'
                        std_out, std_err, ret_code = run_subprocess(script_command)
                        logger.debug(std_out)
                        logger.debug_error(std_err)
                    except subprocess.CalledProcessError as e:
                        logger.info_error(f'{self.NAME}: user {script_name} script return with {e.returncode}: {e}')
                        logger.info(e.output)
                        logger.info_error(e.stderr)

    def pre_processing(self, **kwargs):
        self.__run_user_script(ParallelCompilerConfig.PRE_PROCESSING_FILE_NAME)

    def post_processing(self, **kwargs):
        self.__run_user_script(ParallelCompilerConfig.POST_PROCESSING_FILE_NAME)
