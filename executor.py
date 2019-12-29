import os, subprocess
import run_job

class Job:
    def __init__(self, file_path, binary_file_path, args=None, combination=None, sections_runtime=None):
        self.file_path = file_path
        self.binary_file_path = binary_file_path
        self.combination = combination
        self.sections_runtime = sections_runtime
        self.args = args
        #(compiler_type,compile_flags,env_var)

    def get_file_path(self):
        return self.file_path

    def get_binary_file_path(self):
        return self.binary_file_path

    def get_args(self):
        return self.args



class Executor:

    @staticmethod
    def execute_job(serial_job, jobs):

       output_file=run_job.run_with_sbatch(serial_job.get_binary_file_path(),serial_job.get_args())
       output_file_path = os.path.abspath(output_file)


        for job in jobs:

        #run serial
        batch_file = self.__make_batch_file(self.serial_job.get_binary_file_path())
        n = 0

        for job in self.serial_job+self.jobs:
            job_name = os.path.splitext(job.get_file_path())[0]
            job_des = job.get_binary_file_path()

            sub_proc = subprocess.Popen(['sbatch', '-p', 'grid', '-o', job_name, '-J', job_name,
                                         batch_file, job_des, '-n', str(n), '-j', job_name], cwd=job_des)
            sub_proc.wait()

    def __analysis_output_file(self):
        pass

    def __send_to_database(self):
        pass

