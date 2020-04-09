from compilers.parallelCompiler import ParallelCompiler
from exceptions import CompilationError, FileError, CombinationFailure
import subprocess
import os
import re
from subprocess_handler import run_subprocess
import logger
import traceback


class Par4all(ParallelCompiler):

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None,
                 include_dirs_list=None, is_nas=False, make_obj=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list)
        self.is_nas = is_nas
        self.make_obj = make_obj

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
            logger.info_error(f'{Par4all.__name__} {e}')
            logger.debug_error(f'{traceback.format_exc()}')

    def set_make_obj(self, make_obj):
        self.make_obj = make_obj

    def __run_p4a_process(self):
        files_to_compile = [file_dict['file_full_path'] for file_dict in self.get_file_list()]
        if self.is_nas:
            pips_stub_path = os.path.join(self.get_input_file_directory(), 'common', 'pips_stubs.c')
        else:
            pips_stub_path = os.path.join(self.get_input_file_directory(), 'pips_stubs.c')
        if os.path.exists(pips_stub_path):
            files_to_compile.append(pips_stub_path)
        command = 'PATH=/bin:$PATH p4a -vv ' + ' '.join(files_to_compile)
        if self.is_nas:
            command += ' common/*.c'
        command += ' ' + ' '.join(map(str, super().get_compilation_flags()))
        if self.include_dirs_list:
            command += ' -I ' + ' -I '.join(map(lambda x: os.path.join(self.get_input_file_directory(), str(x)),
                                           self.include_dirs_list))
        try:
            logger.info(f'{Par4all.__name__} start to parallelizing')
            stdout, stderr, ret_code = run_subprocess([command, ], self.get_input_file_directory())
            logger.debug(f'{Par4all.__name__} {stdout}')
            logger.debug_error(f'{Par4all.__name__} {stderr}')
            logger.info(f'{Par4all.__name__} finish to parallelizing')
        except subprocess.CalledProcessError as e:
            raise CombinationFailure(f'par4all return with {e.returncode} code: {str(e)} : {e.output} : {e.stderr}')
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")

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
                                input_file_text = '#ifdef _OPENMP\n#include <omp.h>\n#endif\n{}'.format(input_file_text)
                                f.seek(0)
                                f.write(input_file_text)
                                f.truncate()
        except Exception as e:
            raise CompilationError(str(e) + " files in directory " + self.get_input_file_directory() + " failed to be parallel!")
