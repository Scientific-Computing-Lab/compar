import os
import subprocess
from compiler import Compiler


class Autopar(Compiler):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None, files_list=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory, files_list)

    def compile(self):
        # Parallelizing
        try:
            dir = self.get_input_file_directory()

            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        Autopar.run_autopar(name, dir, self.get_compilation_flags())
            return True

        except Exception as e:
            print("files in directory " + self.get_input_file_directory() + " failed to be parallel!")
            print(e)
            return False

    @staticmethod
    def run_autopar(files_dir, dest_dir, options):
        print("Parallelizing " + files_dir)
        sub_proc = subprocess.Popen(['autoPar'] + options + ["-rose:o", files_dir, files_dir], cwd=dest_dir)
        sub_proc.wait()
        print("Done parallel work")
