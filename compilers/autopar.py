import os
import subprocess
from compiler import Compiler


class Autopar(Compiler):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)

    def compile(self):
        # Parallelizing
        try:
            dir = os.path.abspath(self.get_input_file_directory())
            # dir_name = os.path.basename(dir)
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
        sub_proc = subprocess.Popen(['autoPar'] + options + [files_dir, files_dir], cwd=dest_dir)
        sub_proc.wait()
        print("Done parallel work")
