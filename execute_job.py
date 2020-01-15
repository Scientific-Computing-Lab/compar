import os
import re
import subprocess
# import threading
import time

AMD_OPTERON_PROCESSOE_6376 = list(range(1, 15))
INTEL_XEON_CPU_E5_2683_V4 = list(range(16, 19)) + list(range(20, 24))#no 15
INTEL_XEON_GOLD_6130_CPU = list(range(25, 36))
GRID = AMD_OPTERON_PROCESSOE_6376 + INTEL_XEON_CPU_E5_2683_V4
CLUSTES = INTEL_XEON_GOLD_6130_CPU
MIXEDP = GRID + CLUSTES

class Execute_job:
    #TODO: need to ask if it is ok (yoel)
    MY_BUSY_NUDE_NUMBER_LIST = []

    def __init__(self, job):
        self.job = job
        self.node_number_list = INTEL_XEON_CPU_E5_2683_V4
        self.run_node_number = 0

    def get_job(self):
        return self.job

    def set_job(self, job):
        self.job = job

    def get_node_number_list(self):
        return self.node_number_list

    def set_run_node_number(self, num):
        self.run_node_number = num

    def get_run_node_number(self):
        return self.run_node_number

    @staticmethod
    def get_list_of_busy_nodes_numbers_from_squeue():
        cmd = 'squeue | grep node'
        squeue = subprocess.check_output(cmd, shell=True)
        squeue_text = [x for x in str(squeue).split(" ") if x != '']
        node_lists_in_use = []
        for word in squeue_text:
            if re.search("node\[([0-9]+|([0-9]+\-[0-9]+))+((,[0-9]+\-[0-9]+)|(,[0-9]+))*\]|node[0-9]+", word):
                node_lists_in_use.append(word)
        temp = []
        for word in node_lists_in_use:
            temp = temp + (list(re.findall("[0-9]+\-[0-9]+|[0-9]+", word)))
        nodes_number_in_use = []
        for word in temp:
            if re.search("[0-9]+\-[0-9]+", word):
                num = word.split("-")
                nodes_number_in_use = nodes_number_in_use + list(range(int(num[0]), int(num[1]) + 1))
            else:
                nodes_number_in_use.append(int(word))
        return list(set(nodes_number_in_use))

    def __get_free_node_number_list(self):
        busy_node_number_list = Execute_job.get_list_of_busy_nodes_numbers_from_squeue()
        free_node_number_list = [num for num in self.get_node_number_list() if num not in busy_node_number_list]
        return [num for num in free_node_number_list if num not in Execute_job.MY_BUSY_NUDE_NUMBER_LIST]

    def __get_free_node_number(self):
        free_node_number_list = self.__get_free_node_number_list()
        if not free_node_number_list:
            # TODO: all node are busy
            my_busy_node_number = Execute_job.MY_BUSY_NUDE_NUMBER_LIST
            if not my_busy_node_number:
                # TODO:error no node available (need to get random val a index)
                pass
            return my_busy_node_number[0]

        return free_node_number_list[0]

    @staticmethod
    def has_nodelist_flag_in_slurm_parameters(slurm_parameters):
        if not slurm_parameters:
            return False
        for param in slurm_parameters:
            if re.search("^--nodelist=", param):
                return True
        return False

    def add_nodelist_flag_into_slurm(self, user_slurm_parameters):

        if not Execute_job.has_nodelist_flag_in_slurm_parameters(user_slurm_parameters):
            new_slurm_parameters = user_slurm_parameters.copy()
            node_number = self.__get_free_node_number()
            self.set_run_node_number(node_number)
            flag = '--nodelist='
            if node_number < 10:
                flag = flag + "node00" + str(node_number)
            elif node_number < 100:
                flag = flag + "node0" + str(node_number)
            else:
                flag = flag + "node" + str(node_number)
            new_slurm_parameters.append(flag)
            Execute_job.MY_BUSY_NUDE_NUMBER_LIST.append(node_number)
            return new_slurm_parameters
        return user_slurm_parameters.copy()

    def run(self, user_slurm_parameters):
        self.__run_with_sbatch(user_slurm_parameters)
        self.__analysis_output_file()

    def __run_with_sbatch(self, user_slurm_parameters):
        slurm_parameters = self.add_nodelist_flag_into_slurm(user_slurm_parameters)
        dir_path = self.get_job().get_directory_path()
        dir_name = os.path.basename(dir_path)
        sbatch_script_file = self.__make_sbatch_script_file()

        x_file = dir_name + ".x"
        log_file = dir_name + ".log"
        x_file_path = os.path.join(dir_path, x_file)
        log_file_path = os.path.join(dir_path, log_file)
        slurm_parameters = " ".join(slurm_parameters)
        cmd = 'sbatch {0} -o {1} {2} {3} {4} ' \
            .format(slurm_parameters,
                    log_file_path,
                    sbatch_script_file,
                    x_file_path,
                    self.get_job().get_exec_file_args())

        result = subprocess.check_output(cmd, shell=True)
        # set job id
        result = re.findall('[0-9]', str(result))
        result = ''.join(result)
        self.get_job().set_job_id(result)

        # thread_name = threading.current_thread().getName()
        cmd = "squeue | grep {0}".format(self.get_job().get_job_id())
        while os.system(cmd) == 0:
            time.sleep(30)
            
        if Execute_job.MY_BUSY_NUDE_NUMBER_LIST:
            Execute_job.MY_BUSY_NUDE_NUMBER_LIST.remove(self.get_run_node_number())

    def __make_sbatch_script_file(self):
        batch_file_path = os.path.join(self.get_job().get_directory_path(), 'batch_job.sh')
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
        for root, dirs, files in os.walk(self.get_job().get_directory_path()):
            for file in files:
                if re.search("_run_time_result.txt$", file):
                    file_name = str(file.split("_run_time_result.txt")[0]) + ".c"
                    file_full_path = os.path.join(root, file)
                    self.get_job().set_file_results(file_name)
                    try:
                        with open(file_full_path, 'r') as input_file:
                            for line in input_file:
                                if ":" in line:
                                    line = line[line.find(last_string) + len(last_string)::].replace('\n', '').split(':')
                                    self.get_job().set_loop_in_file_results(file_name, line[0], line[1])
                    except OSError as e:
                        raise Exception(str(e))
