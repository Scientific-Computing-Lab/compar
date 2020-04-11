from abc import ABC, abstractmethod
from compilers.compiler import Compiler
from exceptions import CompilationError


class ParallelCompiler(Compiler, ABC):
    NAME = ''

    def __init__(self, version, input_file_directory=None, compilation_flags=None, file_list=None,
                 include_dirs_list=None):
        super().__init__(version, input_file_directory, compilation_flags)
        self._file_list = file_list
        self.include_dirs_list = include_dirs_list

    def initiate_for_new_task(self, compilation_flags, input_file_directory, file_list):
        super().initiate_for_new_task(compilation_flags, input_file_directory)
        self.set_file_list(file_list)

    def set_file_list(self, file_list):
        self._file_list = file_list

    def get_file_list(self):
        return self._file_list

    def compile(self):
        if not self.get_file_list():
            raise CompilationError("Missing file_list to compile!")
        if not self.get_input_file_directory():
            raise CompilationError("Missing working directory!")

    @abstractmethod
    def pre_processing(self, **kwargs):
        pass

    @abstractmethod
    def post_processing(self, **kwargs):
        pass
