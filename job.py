class Job:
    """
    dir - is the name of the directory that contion the files of the job
    """
    def __init__(self, directory, args=None, combination=None, sections_runtime={}):
        self.directory = directory
        self.combination = combination
        self.sections_runtime = sections_runtime
        self.args = args
        #(compiler_type,compile_flags,env_var)

    def get_dir(self):
        return self.directory

    def get_args(self):
        return self.args

    def get_sections_runtime(self):
        return self.sections_runtime

    def get_loop_time(self, loop_name):
        return self.sections_runtime[loop_name]

    def set_sections_runtime(self, label, time):
        self.sections_runtime[label] = time