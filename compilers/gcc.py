from compilers.binaryCompiler import BinaryCompiler


class Gcc(BinaryCompiler):
    NAME = 'gcc'

    def __init__(self, version, compilation_flags=None, main_c_file=None, input_file_directory=None):
        BinaryCompiler.__init__(self, "gcc", version, compilation_flags, main_c_file, input_file_directory)
