import os
import subprocess
from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, CombinationFailure
from subprocess_handler import run_subprocess
import logger


class Autopar(ParallelCompiler):

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None,
                 include_dirs_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list)

    def compile(self):
        super().compile()
        # Parallelizing
        try:
            for file in self.get_file_list():
                self.run_autopar(file["file_name"], file["file_full_path"], self.get_compilation_flags())
            return True
        except subprocess.CalledProcessError as e:
            raise CombinationFailure(f'autopar return with {e.returncode} code: {str(e)} : {e.output} : {e.stderr}')
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() +
                                   " failed to be parallel!")

    def run_autopar(self, file_name, file_full_path, options):
        logger.info(f'{Autopar.__name__} start to parallelizing {file_name}')
        command = 'autoPar'
        if self.include_dirs_list:
            command += ' -I' + ' -I'.join(map(lambda x: os.path.join(self.get_input_file_directory(), str(x)),
                                              self.include_dirs_list))
        command += f' {" ".join(options)} -c {file_name}'
        stdout, stderr, ret_code = run_subprocess([command], os.path.dirname(file_full_path))
        dir, file_name = os.path.split(file_full_path)
        parallel_file_full_path = os.path.join(dir, f'rose_{file_name}')
        if os.path.exists(parallel_file_full_path):
            os.remove(file_full_path)
            os.rename(parallel_file_full_path, file_full_path)
        logger.debug(f'{Autopar.__name__} {stdout}')
        logger.debug_error(f'{Autopar.__name__} {stderr}')
        logger.info(f'{Autopar.__name__} finish to parallelizing {file_name}')
