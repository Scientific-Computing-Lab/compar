from compilers.parallelCompiler import ParallelCompiler


class Dummy(ParallelCompiler):
    NAME = 'dummy'

    def __init__(self, version: str, compilation_flags: list = None, input_file_directory: str = None,
                 file_list: list = None, include_dirs_list: list = None, **kwargs):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list, **kwargs)

    def compile(self):
        super().compile()

    def pre_processing(self, **kwargs):
        super().pre_processing(**kwargs)

    def post_processing(self, **kwargs):
        super().post_processing(**kwargs)
