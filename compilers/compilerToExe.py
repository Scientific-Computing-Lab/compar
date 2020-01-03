from compiler import Compiler
import os
import subprocess


class CompilerToExe(Compiler):

    def __init__(self, compiler_name, version, compilation_flags, main_c_file, input_file_directory, output_file_directory=None):
        if compilation_flags in ["", None]:
            compilation_flags = []
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)
        self._compiler_name = compiler_name
        self._main_c_file = main_c_file

    def get_compiler_name(self):
        return self._compiler_name

    def set_compiler_name(self, compiler_name):
        self._compiler_name = compiler_name

    def get_main_c_file(self):
        return self._main_c_file

    def set_main_c_file(self, main_c_file):
        self._main_c_file = main_c_file

    def compile(self):
        # Compiling
        try:
            self.run_compiler()
            return True

        except Exception as e:
            print(self.get_main_c_file() + " failed to be compiled!")
            print(e)
            return False

    def run_compiler(self):
        input_file_path_only = os.path.dirname(self.get_input_file_directory())
        dir_name = os.path.basename(input_file_path_only)
        input_file_path = os.path.join(self.get_input_file_directory(), self.get_main_c_file())

        print("Compiling " + self.get_main_c_file())
        sub_proc = subprocess.Popen([self.get_compiler_name()] + ["-fopenmp"] + self.get_compilation_flags() +
                                    [input_file_path] +["-o" + " " + dir_name + ".x"],
                                    cwd=self.get_input_file_directory())
        sub_proc.wait()
        print("Done Compile work")
