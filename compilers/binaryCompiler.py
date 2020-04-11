from compilers.compiler import Compiler
import os
import subprocess
from exceptions import CompilationError, CombinationFailure
from subprocess_handler import run_subprocess
import logger


class BinaryCompiler(Compiler):
    NAME = ''

    def __init__(self, compiler_name, version, compilation_flags=None, input_file_directory=None, main_c_file=None):
        super().__init__(version, compilation_flags, input_file_directory)
        self._compiler_name = compiler_name
        self._main_c_file = main_c_file

    def initiate_for_new_task(self, compilation_flags, input_file_directory, main_c_file):
        super().initiate_for_new_task(compilation_flags, input_file_directory)
        self.set_main_c_file(main_c_file)

    def get_compiler_name(self):
        return self._compiler_name

    def set_compiler_name(self, compiler_name):
        self._compiler_name = compiler_name

    def get_main_c_file(self):
        return self._main_c_file

    def set_main_c_file(self, main_c_file):
        self._main_c_file = main_c_file

    def compile(self):
        if not self.get_main_c_file():
            raise CompilationError("Missing main_file argument to compile!")
        if not self.get_input_file_directory():
            raise CompilationError("Missing working directory!")
        # Compiling
        try:
            self.run_compiler()
            return True
        except subprocess.CalledProcessError as ex:
            std_out, std_err = ex.output, ex.stderr
            if isinstance(std_out, bytes):
                std_out = str(ex.output, encoding='utf-8')
            if isinstance(std_err, bytes):
                std_err = str(ex.stderr, encoding='utf-8')
            raise CombinationFailure(self._compiler_name +
                                     f' return with {ex.returncode} code: {str(ex)} : {std_out} : {std_err}')
        except Exception as e:
            raise CompilationError(str(e) + " " + self.get_main_c_file() + " failed to be compiled!")

    def run_compiler(self):
        input_file_path_only = os.path.dirname(self.get_input_file_directory() + os.path.sep)
        dir_name = os.path.basename(input_file_path_only)

        logger.info(f'{BinaryCompiler.__name__} start to compiling {self.get_main_c_file()}')
        command = [self.get_compiler_name(), "-fopenmp"] + self.get_compilation_flags()
        command += [self.get_main_c_file(), "-o", dir_name + ".x"]
        stdout, stderr, ret_code = run_subprocess(command, self.get_input_file_directory())
        logger.debug(f'{BinaryCompiler.__name__} {stdout}')
        logger.debug_error(f'{BinaryCompiler.__name__} {stderr}')
        logger.info(f'{BinaryCompiler.__name__} finish to compiling {self.get_main_c_file()}')
