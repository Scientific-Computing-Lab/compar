from compilers.compiler import Compiler
from exceptions import CompilationError
import subprocess
import os
import re


class Par4all(Compiler):
    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None,
                 files_list=None, include_dirs_list=None):
        super().__init__(version, compilation_flags, input_file_directory, output_file_directory, files_list)
        self.__include_dirs_list = include_dirs_list

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
        command = ['p4a', '-v', '--log', '-O', file_path_to_compile]
        if self.__include_dirs_list:
            command += ['-I', ] + self.__include_dirs_list
        subprocess.run(command, shell=True, cwd=self.get_input_file_directory())

    def compile(self):
        if not self.files_list:
            raise CompilationError('There is no file to compile')
        for file_dict in self.files_list:
            self.__run_p4a_process(file_dict['file_path'])  # TODO: check if the key is correct
            file_name, extension = os.path.splitext(file_dict['file_path'])  # TODO: check if the key is correct
            name_to_replace = file_name + '.p4a' + extension
            os.rename(name_to_replace, file_dict['file_path'])  # TODO: check if the key is correct
            self.__remove_bswap_function( file_dict['file_path'])  # TODO: check if the key is correct
