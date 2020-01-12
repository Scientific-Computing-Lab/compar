from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError
import subprocess
import os
import re
import shutil


class Par4all(ParallelCompiler):

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None, include_dirs_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)
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
        folder_path = os.path.dirname(file_path_to_compile)
        results_folder = os.path.join(folder_path, 'parallel_results')
        os.mkdir(results_folder)
        shutil.copyfile(file_path_to_compile, os.path.join(results_folder, os.path.basename(file_path_to_compile)))
        pips_stubs_file = os.path.join(folder_path, 'pips_stubs.c')
        if os.path.exists(pips_stubs_file):
            shutil.copyfile(pips_stubs_file, os.path.join(results_folder, 'pips_stubs.c'))
        files_to_compile = results_folder + os.sep + '*.c'
        command = 'module load par4all; source $set_p4a_env; p4a -v --log -O ' + str(files_to_compile)
        command += ' '.join(map(str, super().get_compilation_flags()))
        if self.__include_dirs_list:
            command += '-I ' + ' '.join(map(str, self.__include_dirs_list))
        subprocess.run(command, shell=True, cwd=folder_path)

    def compile(self):
        try:
            super().compile()
            for file_dict in self.get_file_list():
                self.__run_p4a_process(file_dict['file_full_path'])
                file_name, extension = os.path.splitext(file_dict['file_full_path'])
                name_to_replace = file_name + '.p4a' + extension
                os.rename(name_to_replace, file_dict['file_full_path'])
                self.__remove_bswap_function(file_dict['file_full_path'])
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")
