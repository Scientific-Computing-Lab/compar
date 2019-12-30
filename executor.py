import os, subprocess

from concurrent.futures import ThreadPoolExecutor

class Job:
    '''
    dir - is the name of the directory that contion the files of the job
    '''
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

    def get_loop_time(self,loop_name):
        return self.sections_runtime[loop_name]

    def set_sections_runtime(self, loop_name, time):
        self.sections_runtime[loop_name]=time

class Processor:

    def __init__(self, job):
        self.job = job

    def get_job(self):
        return self.job

    def run(self):
        self.__run_with_sbatch()
        self.analysis_output_file()

    def __run_with_sbatch(self, times=1, slurm_partition='grid'):
        '''
        :param times: The number of times you want to run the Job. Default=1
        :param slurm_partition:The SLURM option . default="grid"
        :return:
        Look for an .x file inside the folder of Job (job.get_dir()).
        Send it to run on sbatch.
        Save the output files in the Job dir.
        '''
        batch_file = self.__make_batch_file()
        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if os.path.splitext(file)[1] == '.x':
                    file_name = os.path.basename(os.path.splitext(file)[0])
                    file_path = os.path.abspath(file)
                    for i in range(0, times):
                        output_file_name = file_name + '_' + str(i)
                        sub_proc = subprocess.Popen(
                            ['sbatch', '-p', slurm_partition, '-o', output_file_name, '-J', output_file_name,
                             batch_file, file_path, self.get_job().get_args()], cwd=self.get_job().get_dir())

                        sub_proc.wait()

    def __make_batch_file(self):
        batch_file_path = os.path.join(os.path.abspath(self.get_job().get_dir()), 'batch_job.sh')
        batch_file = open(batch_file_path, 'w')
        batch_file.write(
            '#!/bin/bash\n'
            + '#SBATCH --exclusive\n'
            + '$@\n'
        )

    def __analysis_output_file(self):
        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if os.path.splitext(file)[1] == '.txt':
                    f = open(file, "r")
                    for x in f:
                        if(x == "what yoni or may choose (LOOP name #time) "):
                            #merfassim !!!



class Executor:
    @staticmethod
    def execute_jobs(jobs, number_of_threads=4):
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        for job in jobs():
            pool.submit(Processor(job).run())
        pool.shutdown()
        return jobs



