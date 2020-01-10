from compilers.binaryCompiler import BinaryCompiler


class Icc(BinaryCompiler):

    def __init__(self, version, compilation_flags=None, main_c_file=None, input_file_directory=None):
        super().__init__("icc", version, compilation_flags, main_c_file, input_file_directory)

