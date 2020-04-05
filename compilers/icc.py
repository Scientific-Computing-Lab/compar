from compilers.binaryCompiler import BinaryCompiler
import os
import subprocess
from subprocess_handler import run_subprocess


class Icc(BinaryCompiler):

    def __init__(self, version, compilation_flags=None, main_c_file=None, input_file_directory=None):
        super().__init__("icc", version, compilation_flags, main_c_file, input_file_directory)

    def run_compiler(self):
        input_file_path_only = os.path.dirname(self.get_input_file_directory() + os.path.sep)
        dir_name = os.path.basename(input_file_path_only)

        print("Compiling " + self.get_main_c_file())
        stdout, stderr, ret_code = run_subprocess([self.get_compiler_name()] + ["-fopenmp"]
                                         + self.get_compilation_flags() + [self.get_main_c_file()]
                                         + ["-o"] + [dir_name + ".x"], self.get_input_file_directory())
        print(self._compiler_name + ' compilation output: ' + str(stdout))
        print("Done Compile work")
