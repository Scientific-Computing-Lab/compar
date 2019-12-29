import os, subprocess


class Job:
    def __init__(self, file_path, binary_file_path, combination=None, sections_runtime=None):
        self.file_path = file_path
        self.binary_file_path = binary_file_path
        self.combination = combination
        self.sections_runtime = sections_runtime
         #(compiler_type,compile_flags,env_var)

    def get_file_path(self):
        return self.file_path

    def get_binary_file_path(self):
        return self.binary_file_path


class Executor:
    def __init__(self, serial_job, jobs):
        self.serial_job = serial_job
        self.jobs = jobs

    def execute_job(self):
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

    def __make_batch_file(self, job_dir):
        batch_file_path = os.path.join(job_dir, 'batch_job.sh')
        batch_file = open(batch_file_path, 'w')
        batch_file.write(
            '#!/bin/bash\n'
            + '#SBATCH --exclusive\n'
            + '$@\n'
        )
        batch_file.close()
        return batch_file_path
