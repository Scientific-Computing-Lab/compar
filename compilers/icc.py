from compiler import Compiler
import os
import subprocess


class Icc(Compiler):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)

    def compile(self):
        # Compiling
        try:
            dir = os.path.abspath(self.get_input_file_directory())
            # dir_name = os.path.basename(dir)
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        Icc.run_autopar(name, dir, self.get_compilation_flags())
            return True

        except Exception as e:
            print("files in directory " + self.get_input_file_directory() + " failed to be compiled!")
            print(e)
            return False

    @staticmethod
    def run_icc(file_name, file_dir, options):
        print("Compiling " + file_name)
        sub_proc = subprocess.Popen(['icc'] + [options, file_name, "-o", file_name+".x"], cwd=file_dir)
        sub_proc.wait()
        print("Done Compile work")
