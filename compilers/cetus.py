from compilers.compiler import Compiler
import subprocess
import os


class Cetus(Compiler):

    def __init__(self, version, input_filename_directory, output_filename_directory, compilation_flags):
        Compiler.__init__(self, version, input_filename_directory, output_filename_directory, compilation_flags)

    def compile(self):
        try:
            dir = os.path.abspath(self.get_input_filename_directory())
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        sub_proc = subprocess.Popen(['cetus'] + self.get_compilation_flags() + [name], cwd=dir)
                        sub_proc.wait()
            return True

        except Exception as e:
            print("files in directory " + self.get_input_filename_directory() + " failed to be parallel!")
            print(e)
            return False