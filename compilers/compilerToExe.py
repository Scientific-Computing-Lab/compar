from compiler import Compiler
import os
import subprocess


class CompilerToExe(Compiler):

    def __init__(self, compiler_name, version, compilation_flags, input_file_directory, output_file_directory=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)
        self._compiler_name = compiler_name

    def get_compiler_name(self):
        return self._compiler_name

    def set_compiler_name(self, compiler_name):
        self._compiler_name = compiler_name

    def compile(self):
        # Compiling
        try:
            dir = os.path.abspath(self.get_input_file_directory())
            print(dir)
            # dir_name = os.path.basename(dir)
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        self.run_compiler(name, dir, self.get_compilation_flags())
            return True

        except Exception as e:
            print("files in directory " + self.get_input_file_directory() + " failed to be compiled!")
            print(e)
            return False

    def run_compiler(self, file_name, file_dir, options):
        print("Compiling " + file_name)

        if options in ["", None]:
            options = []

        sub_proc = subprocess.Popen([self.get_compiler_name()]+ ["-fopenmp"] + options + [file_name] +
                                    ["-o" + " " + self.get_input_file_directory()+".x"], cwd=file_dir)
        sub_proc.wait()
        print("Done Compile work")

