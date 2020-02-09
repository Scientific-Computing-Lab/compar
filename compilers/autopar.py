import os
import subprocess
from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, CombinationFailure


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
        except subprocess.CalledProcessError as e:
            raise CombinationFailure(f'autopar return with {e.returncode} code: {str(e)} : {e.output} : {e.stderr}')
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")

    @staticmethod
    def run_autopar(file_name, file_full_path, options):
        print("Parallelizing " + file_name)
        command = [f'module load autopar; autoPar {" ".join(options)} -c {file_name}']
        output = subprocess.check_output(command, shell=True, cwd=os.path.dirname(file_full_path))
        print('autopar compilation output: ' + str(output))
        print("Done parallel work")
