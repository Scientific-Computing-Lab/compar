from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, CombinationFailure
import subprocess
import shutil
import os
import exceptions as e


class Cetus(ParallelCompiler):

    def __init__(self, version, input_file_directory=None, compilation_flags=None, file_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)

    def compile(self):
        super().compile()
        try:
            for file in self.get_file_list():
                Cetus.replace_line_in_code(file["file_full_path"], '#include <omp.h>', '')
                cwd_path = os.path.dirname(file["file_full_path"])
                output = subprocess.check_output(['module load cetus; cetus {} {}'.format(
                    " ".join(self.get_compilation_flags()), file["file_name"])], shell=True, cwd=cwd_path)
                print('cetus compilation output: ' + str(output))
                # Replace file from cetus output folder into original file folder
                if os.path.isdir(os.path.join(cwd_path, "cetus_output")):
                    src_file = os.path.join(cwd_path, "cetus_output", file["file_name"])
                    dst_file = file["file_full_path"]
                    shutil.copy(src_file, dst_file)
                    shutil.rmtree(os.path.join(cwd_path, "cetus_output"))

                Cetus.inject_line_in_code(file["file_full_path"], '#include <omp.h>')
            return True
        except subprocess.CalledProcessError as ex:
            raise CombinationFailure(f'par4all return with {ex.returncode} code: {str(ex)} : {ex.output} : {ex.stderr}')
        except Exception as ex:
            raise CompilationError(str(ex) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")

    @staticmethod
    def replace_line_in_code(file_full_path, old_line, new_line):
        with open(file_full_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        c_code = c_code.replace(old_line, new_line)
        try:
            with open(file_full_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))

    @staticmethod
    def inject_line_in_code(file_full_path, new_line):
        with open(file_full_path, 'r') as input_file:
            c_code = input_file.read()
        e.assert_file_is_empty(c_code)
        c_code = new_line + c_code
        try:
            with open(file_full_path, 'w') as output_file:
                output_file.write(c_code)
        except OSError as err:
            raise e.FileError(str(err))