import os
import subprocess
from compilers.parallelCompiler import ParallelCompiler


class Autopar(ParallelCompiler):

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)

    def compile(self):
        super().compile()
        # Parallelizing
        try:
            for file in self.get_file_list():
                Autopar.run_autopar(file["file_name"], file["file_full_path"], self.get_compilation_flags())
            return True

        except Exception as e:
            print("files in directory " + self.get_input_file_directory() + " failed to be parallel!")
            print(e)
            return False

    @staticmethod
    def run_autopar(file_name, file_full_path, options):
        print("Parallelizing " + file_name)
        sub_proc = subprocess.Popen(['autoPar'] + options + ["-rose:o", file_name, file_name], cwd=os.path.dirname(file_full_path))
        sub_proc.wait()
        print("Done parallel work")
