class Job:
    def __init__(self,file_path, binary_file_path, combination=None, sections_runtime=None):
        self.file_path = file_path
        self.binary_file_pat = binary_file_path
        self.combination = combination
        self.sections_runtime = sections_runtime
         #(compiler_type,compile_flags,env_var)


class Executor:
    def __init__(self, serial_job, jobs):
        self.serial_job = serial_job
        self.jobs = jobs

    def execute_job(self):

        #run serial
        for job in self.jobs:
            pass
            #start sbach and white using thread

    def __analysis_output_file(self):
        pass

    def __send_to_database(self):
        pass
