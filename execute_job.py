import os
import re
import subprocess
import threading
import time


class Execute_job:

    def __init__(self, job, log_file):
        self.job = job
        self.log_file = log_file #####

    def get_job(self):
        return self.job

    def run(self):
        self.__run_with_sbatch()
        self.__analysis_output_file()

    def __run_with_sbatch(self, times=1, slurm_partition='grid'):
        """
        :param times: The number of times you want to run the Job. Default=1
        :param slurm_partition:The SLURM option . default="grid"
        :return:
        Look for an .x file inside the folder of Job (job.get_dir()).
        Send it to run on sbatch.
        Save the output files in the Job dir.
        """

        batch_file = self.__make_batch_file()

        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if os.path.splitext(file)[1] == '.x':
                    file_name = os.path.basename(os.path.splitext(file)[0])
                    file_path = os.path.abspath(file)
                    for i in range(0, times):
                        output_file_name = file_name + '_' + str(i)
                        self.log_file.flush()
                        sub_proc = subprocess.Popen(
                            ['sbatch', '-p', slurm_partition, '-o', output_file_name, '-J', output_file_name,
                             batch_file, file_path, self.get_job().get_exec_file_args()], cwd=self.get_job().get_dir(),
                            stdout=self.log_file, stderr=self.log_file, shell=False)
                        sub_proc.wait()
                        self.get_job().set_job_id(self.log_file.readline())
                        self.log_file.close()

                        thread_name = threading.current_thread().getName()
                        while not os.path.exists(output_file_name):
                            print("I am thread " + str(thread_name) + " and i am going to sleep")
                            time.sleep(30)
                            print("I am thread " + str(thread_name) + " and i am awake!")
                        print("I am thread " + str(thread_name) + " and i am FINISH!!!!!!")

    def __make_batch_file(self):
        batch_file_path = os.path.join(os.path.abspath(self.get_job().get_dir()), 'batch_job.sh')
        batch_file = open(batch_file_path, 'w')
        batch_file.write(
            '#!/bin/bash\n'
            + '#SBATCH --exclusive\n'
            + '$@\n'
        )
        return batch_file_path

    def __analysis_output_file(self):
        last_string = 'loop '
        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if re.search("_time_results.txt$", file):
                    file_name = file.split("_time_results.txt")[0]+".c"
                    try:
                        with open(file, 'r') as input_file:
                            for line in input_file:
                                line = line[line.find(last_string) + len(last_string)::].replace('\n', '').split(':')
                                self.get_job().set_loop_run_time_in_file_results(file_name, line[0], line[1])

                    except OSError as e:
                        raise Exception(str(e))
