import os
import subprocess
from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError


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
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")

    @staticmethod
    def run_autopar(file_name, file_full_path, options):
        print("Parallelizing " + file_name)
        command = ['module load autopar; autoPar {0} -rose:o {1} {2}'.format(" ".join(options), file_name, file_name)]
        subprocess.run(command, shell=True, cwd=os.path.dirname(file_full_path))
        print("Done parallel work")
