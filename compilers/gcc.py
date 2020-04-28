from compilers.binaryCompiler import BinaryCompiler


class Gcc(BinaryCompiler):
    NAME = 'gcc'

    def __init__(self, version: str, compilation_flags: list = None, main_c_file: str = None,
                 input_file_directory: str = None):
        BinaryCompiler.__init__(self, self.NAME, version, compilation_flags, input_file_directory, main_c_file)
