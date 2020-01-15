from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, FileError, CombinationFailure
import subprocess
import os
import re


class Par4all(ParallelCompiler):

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None, include_dirs_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)
        self.__include_dirs_list = include_dirs_list

    @staticmethod
    def remove_code_from_file(file_path, code_to_be_removed):
        try:
            with open(file_path, 'r+') as f:
                file_content = f.read()
                file_content = file_content.replace(code_to_be_removed, '')
                f.seek(0)
                f.write(file_content)
                f.truncate()
        except Exception as e:
            raise FileError(str(e))

    @staticmethod
    def inject_code_at_the_top(file_path, code_to_be_injected):
        try:
            with open(file_path, 'r+') as f:
                file_content = f.read()
                file_content = code_to_be_injected + '\n' + file_content
                f.seek(0)
                f.write(file_content)
                f.truncate()
        except Exception as e:
            raise FileError(str(e))

    @staticmethod
    def __remove_bswap_function(file_path):
        bswap_regex = re.compile(r'static __uint64_t __bswap_64[^\}]*\}', re.DOTALL)
        try:
            with open(file_path, 'r+') as f:
                content = f.read()
                if bswap_regex.match(content):
                    content = bswap_regex.sub('', content)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
        except Exception as e:
            print(e)

    def __run_p4a_process(self, file_path_to_compile):
        files_to_compile = [file_path_to_compile, ]
        pips_stub_path = os.path.join(self.get_input_file_directory(), 'pips_stubs.c')
        if os.path.exists(pips_stub_path):
            files_to_compile.append(pips_stub_path)
        command = 'module load par4all && source $set_p4a_env && p4a -v -O  ' + ' '.join(files_to_compile)
        command += ' '.join(map(str, super().get_compilation_flags()))
        if self.__include_dirs_list:
            command += '-I ' + ' '.join(map(str, self.__include_dirs_list))
        try:
            output = subprocess.check_output([command, ], shell=True, cwd=self.get_input_file_directory())
            print('par4all compilation output: ' + str(output))
        except subprocess.CalledProcessError as e:
            raise CombinationFailure(f'par4all return with {e.returncode} code: {str(e)} : {e.output} : {e.stderr}')
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")

    def compile(self):
        try:
            super().compile()
            for file_dict in self.get_file_list():
                self.remove_code_from_file(file_dict['file_full_path'], '#include <omp.h>')
                self.__run_p4a_process(file_dict['file_full_path'])
                file_name, extension = os.path.splitext(file_dict['file_full_path'])
                name_to_replace = file_name + '.p4a' + extension
                os.rename(name_to_replace, file_dict['file_full_path'])
                self.inject_code_at_the_top(file_dict['file_full_path'], '#include <omp.h>')
                self.__remove_bswap_function(file_dict['file_full_path'])
                compiled_pips_stubs = os.path.join(self.get_input_file_directory(), 'pips_stubs.p4a.c')
                if os.path.exists(compiled_pips_stubs):
                    os.remove(compiled_pips_stubs)
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")
