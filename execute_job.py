import os
import re
import subprocess
#import threading
import time


class Execute_job:

    def __init__(self, job):
        self.job = job

    def get_job(self):
        return self.job

    def set_job(self, job):
        self.job = job

    def run(self):
        self.__run_with_sbatch()
        self.__analysis_output_file()

    def __run_with_sbatch(self, slurm_parameters):
        """
        :param times: The number of times you want to run the Job. Default=1
        :param slurm_partition:The SLURM option . default="grid"
        :return:
        Look for an .x file inside the folder of Job (job.get_dir()).
        Send it to run on sbatch.
        Save the output files in the Job dir.
        """
        sbatch_script_file = self.__make_sbatch_script_file()

        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if os.path.splitext(file)[1] == '.x':
                    log_file_name = "log_"+str(os.path.basename(file))

                    cmd='sbatch {0} -o {1} {2} {3} {4} '\
                        .format(slurm_parameters,
                                log_file_name,
                                sbatch_script_file,
                                file,
                                self.get_job().set_exec_file_args())

                    result = subprocess.check_output(cmd, shell=True)
                    #set job id
                    result = re.findall('[0-9]', str(result))
                    result = ''.join(result)
                    self.get_job().set_job_id(result)

                    #thread_name = threading.current_thread().getName()
                    while not os.path.exists(log_file_name):
                        time.sleep(30)

    def __make_sbatch_script_file(self):
        batch_file_path = os.path.join(os.path.abspath(self.get_job().get_dir()), 'batch_job.sh')
        batch_file = open(batch_file_path, 'w')
        batch_file.write(
            '#!/bin/bash\n'
            + '#SBATCH --job-name=compar\n'
            + '#SBATCH --partition=grid\n'
            + '#SBATCH --exclusive\n'
            + '$@\n'
        )
        return batch_file_path

    def __analysis_output_file(self):
        last_string = 'loop '
        for root, dirs, files in os.walk(self.get_job().get_dir()):
            for file in files:
                if re.search("_time_results.txt$", file):
                    file_name = str(file.split("_time_results.txt")[0]) + ".c"
                    try:
                        with open(file, 'r') as input_file:
                            for line in input_file:
                                line = line[line.find(last_string) + len(last_string)::].replace('\n', '').split(':')
                                self.get_job().set_loop_run_time_in_file_results(file_name, line[0], line[1])

                    except OSError as e:
                        raise Exception(str(e))
