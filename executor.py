class Job :
    def __init__(self,file_path, binary_file_path, combination =None, sections_runtime =None):
        self.file_path = file_path
        self.binary_file_path=binary_file_path
        self.combination=combination
        #(compiler_type,compile_flags,env_var)
        self.sections_runtime=sections_runtime


class Executor :
    def __init__(self,serial_job,jobs):
        self.serial_job=serial_job
        self.jobs=jobs


    def execute_job(self):

        #run serial
        for job in self.jobs:
            #srat sbach and white using thread
            #


    def __analiysis_output_file(self):

    def __send_to_database(self):
