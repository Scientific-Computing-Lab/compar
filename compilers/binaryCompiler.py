from compiler import Compiler
import os
import subprocess
from exceptions import CompilationError


class BinaryCompiler(Compiler):

    def __init__(self, compiler_name, version, compilation_flags=None, input_file_directory=None, main_c_file=None):
        super().__init__(version, compilation_flags, input_file_directory)
        self._compiler_name = compiler_name
        self._main_c_file = main_c_file

    def initiate_for_new_task(self, compilation_flags, input_file_directory, main_c_file):
        super().initiate_for_new_task(compilation_flags, input_file_directory)
        self.set_main_c_file(self, main_c_file)

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

        except Exception as e:
            print(self.get_main_c_file() + " failed to be compiled!")
            print(e)
            return False

    def run_compiler(self):
        input_file_path_only = os.path.dirname(self.get_input_file_directory() + "/")
        dir_name = os.path.basename(input_file_path_only)

        print("Compiling " + self.get_main_c_file())
        sub_proc = subprocess.Popen([self.get_compiler_name()] + ["-fopenmp"] + self.get_compilation_flags() +
                                    [self.get_main_c_file()] + ["-o" + " " + dir_name + ".x"],
                                    cwd=self.get_input_file_directory())
        sub_proc.wait()
        print("Done Compile work")
