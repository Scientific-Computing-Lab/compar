from abc import ABC, abstractmethod


class Compiler(ABC):
    
    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None, files_list=None):
        self._version = version
        self._input_file_directory = input_file_directory
        self._output_file_directory = output_file_directory
        self._compilation_flags = compilation_flags
        self._files_list = files_list

    @abstractmethod
    def compile(self):
        "implement your own compiler"
        pass

    def update(self, version, compilation_flags, input_file_directory, output_file_directory=None, files_list=None):
        self.set_version(version)
        self.set_compilation_flags(compilation_flags)
        self.set_input_file_directory(input_file_directory)
        self.set__output_file_directory(output_file_directory)
        self.set_files_list(files_list)

    def get_version(self):
        return self._version

    def set_version(self, version):
        self._version = version

    def get_input_file_directory(self):
        return self._input_file_directory
    
    def set_input_file_directory(self, input_file_directory):
        self._input_file_directory = input_file_directory
    
    def get_output_file_directory(self):
        return self._output_file_directory
    
    def set__output_file_directory(self, output_file_directory):
        self._output_file_directory = output_file_directory

    def get_compilation_flags(self):
        return self._compilation_flags

    def set_compilation_flags(self, compilation_flags):
        self._compilation_flags = compilation_flags

    def set_files_list(self, files_list):
        self._files_list = files_list

    def get_files_list(self):
        return self._files_list