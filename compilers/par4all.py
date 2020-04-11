from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, FileError, CombinationFailure
import subprocess
import os
import re
from subprocess_handler import run_subprocess
import logger
import traceback
import shutil


class Par4all(ParallelCompiler):
    NAME = 'par4all'
    PIPS_STUBS_NAME = 'pips_stubs.c'

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None,
                 include_dirs_list=None, is_nas=False, make_obj=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list)
        self.is_nas = is_nas
        self.make_obj = make_obj
        self.files_to_compile = []

    def __copy_pips_stubs_to_folder(self):
        destination_folder_path = self.get_input_file_directory()
        pips_stubs_path = os.path.join('assets', Par4all.PIPS_STUBS_NAME)
        if Par4all.PIPS_STUBS_NAME not in os.listdir(destination_folder_path):
            shutil.copy(pips_stubs_path, destination_folder_path)
        return os.path.join(destination_folder_path, Par4all.PIPS_STUBS_NAME)

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
        bswap_regex = re.compile(r'static __uint64_t __bswap_64[^\}]*\}', flags=re.DOTALL)
        try:
            with open(file_path, 'r+') as f:
                content = f.read()
                if bswap_regex.match(content):
                    content = bswap_regex.sub('', content)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
        except Exception as e:
            logger.info_error(f'Exception at {Par4all.__name__}: {e}')
            logger.debug_error(f'{traceback.format_exc()}')

    def set_make_obj(self, make_obj):
        self.make_obj = make_obj

    def initiate_for_new_task(self, compilation_flags, input_file_directory, file_list):
        super().initiate_for_new_task(compilation_flags, input_file_directory, file_list)
        self.files_to_compile = []

    def __run_p4a_process(self):
        self.files_to_compile += [file_dict['file_full_path'] for file_dict in self.get_file_list()]
        command = 'PATH=/bin:$PATH p4a -vv ' + ' '.join(self.files_to_compile)
        if self.is_nas:
            command += ' common/*.c'
        command += ' ' + ' '.join(map(str, super().get_compilation_flags()))
        if self.include_dirs_list:
            command += ' -I ' + ' -I '.join(map(lambda x: os.path.join(self.get_input_file_directory(), str(x)),
                                                self.include_dirs_list))
        try:
            logger.info(f'{Par4all.__name__} start to parallelizing')
            stdout, stderr, ret_code = run_subprocess([command, ], self.get_input_file_directory())
            log_file_path = os.path.join(self.get_input_file_directory(), 'par4all_output.log')
            logger.log_to_file(f'{stdout}\n{stderr}', log_file_path)
            logger.debug(f'{Par4all.__name__} {stdout}')
            logger.debug_error(f'{Par4all.__name__} {stderr}')
            logger.info(f'{Par4all.__name__} finish to parallelizing')
        except subprocess.CalledProcessError as e:
            std_out, std_err = e.output, e.stderr
            if isinstance(std_out, bytes):
                std_out = str(e.output, encoding='utf-8')
            if isinstance(std_err, bytes):
                std_err = str(e.stderr, encoding='utf-8')
            log_file_path = os.path.join(self.get_input_file_directory(), 'par4all_output.log')
            logger.log_to_file(f'{std_out}\n{std_err}', log_file_path)
            raise CombinationFailure(f'par4all return with {e.returncode} code: {str(e)} : {std_out} : {std_err}')
        except Exception as e:
            raise CompilationError(f"{e}\nfiles in directory {self.get_input_file_directory()} failed to be parallel!")

    def compile(self):
        try:
            super().compile()
            if self.is_nas:
                self.make_obj.make()
                if os.path.exists(self.make_obj.get_exe_full_path()):
                    os.remove(self.make_obj.get_exe_full_path())
                wtime_sgi64_path = os.path.join(self.get_input_file_directory(), 'common', 'wtime_sgi64.c')
                if os.path.exists(wtime_sgi64_path):
                    os.remove(wtime_sgi64_path)
            self.__run_p4a_process()
            for root, dirs, files in os.walk(self.get_input_file_directory()):
                for file in files:
                    full_path = os.path.join(root, file)
                    if file.endswith('.p4a.c'):
                        os.rename(full_path, full_path[0:-6] + '.c')
                        full_path = full_path[0:-6] + '.c'
                        self.__remove_bswap_function(full_path)
                        with open(full_path, "r+") as f:
                            input_file_text = f.read()
                            if '#include <omp.h>' not in input_file_text:
                                input_file_text = f'#ifdef _OPENMP\n#include <omp.h>\n#endif\n{input_file_text}'
                                f.seek(0)
                                f.write(input_file_text)
                                f.truncate()
        except Exception as e:
            raise CompilationError(f"{e}\nFiles in directory {self.get_input_file_directory()} failed to be parallel!")

    def pre_processing(self, **kwargs):
        if 'makefile_obj' in kwargs:
            self.set_make_obj(kwargs['makefile_obj'])
        pips_file_path = self.__copy_pips_stubs_to_folder()
        self.files_to_compile.append(pips_file_path)

    def post_processing(self, **kwargs):
        os.remove(os.path.join(self.get_input_file_directory(), self.PIPS_STUBS_NAME))
