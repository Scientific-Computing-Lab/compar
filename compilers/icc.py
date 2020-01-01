from compilerToExe import CompilerToExe


class Icc(CompilerToExe):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None):
        CompilerToExe.__init__(self, "icc", version, compilation_flags, input_file_directory, output_file_directory)
