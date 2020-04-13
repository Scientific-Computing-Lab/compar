from compilers.parallelCompiler import ParallelCompiler

class Dummy(ParallelCompiler):
    NAME = 'dummy'

    def __init__(self, version, compilation_flags=None, input_file_directory=None, file_list=None,
                 include_dirs_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list, include_dirs_list)

    def compile(self):
        super().compile()

    def pre_processing(self, **kwargs):
        super().pre_processing(**kwargs)

    def post_processing(self, **kwargs):
        super().post_processing(**kwargs)
