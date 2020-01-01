from compilerToExe import CompilerToExe


class Gcc(CompilerToExe):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None):
        CompilerToExe.__init__(self, "GCC", version, compilation_flags, input_file_directory, output_file_directory)

    def compile(self):
        pass
