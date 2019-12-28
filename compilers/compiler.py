from abc import ABC,abstractmethod

class Compiler(ABC):
    
    def __init__(self,version,input_filename,output_filename,compilation_flags):
        self._version = version
        self._input_filename = input_filename
        self._output_filename = output_filename
        self._compilation_flags = compilation_flags

    @abstractmethod
    def compile(self):
        "implement your own compiler"
        pass

    def get_version(self):
        return self._version
    
    def set_version(self,version):
        self._version = version

    def get_input_filename(self):
        return self._input_filename
    
    def set_input_filename(self,input_filename):
        self._input_filename = input_filename
    
    def get_output_filename(self):
        return self._output_filename
    
    def set__output_filename(self,output_filename):
        self._output_filename = output_filename

    def get_compilation_flags(self):
        return self._compilation_flags
    
    def set_compilation_flags(self,compilation_flags):
        self._compilation_flags = compilation_flags