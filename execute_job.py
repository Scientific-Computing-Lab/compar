import os
import re
import subprocess
# import threading
import time
from exceptions import FileError

AMD_OPTERON_PROCESSOE_6376 = list(range(1, 15))
INTEL_XEON_CPU_E5_2683_V4 = list(range(16, 19)) + list(range(20, 24))  # no 15
INTEL_XEON_GOLD_6130_CPU = list(range(25, 36))
GRID = AMD_OPTERON_PROCESSOE_6376 + INTEL_XEON_CPU_E5_2683_V4
CLUSTES = INTEL_XEON_GOLD_6130_CPU
MIXEDP = GRID + CLUSTES


class ExecuteJob:
    #TODO: need to ask if it is ok (yoel)
    MY_BUSY_NODE_NUMBER_LIST = []

    def __init__(self, job, num_of_loops_in_files, db, db_lock, save_results, serial_run_time, relative_c_file_list):
        self.job = job
        self.node_number_list = INTEL_XEON_CPU_E5_2683_V4
        self.run_node_number = 0
        self.num_of_loops_in_files = num_of_loops_in_files
        self.db = db
        self.db_lock = db_lock
        self.save_results = save_results
        self.serial_run_time_dict = serial_run_time  # {(<file_id_by_rel_path>, <loop_label>) : <run_time>, ... }
        self.relative_c_file_list = relative_c_file_list

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
        busy_node_number_list = ExecuteJob.get_list_of_busy_nodes_numbers_from_squeue()
        free_node_number_list = [num for num in self.get_node_number_list() if num not in busy_node_number_list]
        return [num for num in free_node_number_list if num not in ExecuteJob.MY_BUSY_NODE_NUMBER_LIST]

    def __get_free_node_number(self):
        free_node_number_list = self.__get_free_node_number_list()
        if not free_node_number_list:
            # all INTEL nodes are busy so choose from my busy node
            my_busy_node_number = ExecuteJob.MY_BUSY_NODE_NUMBER_LIST
            if not my_busy_node_number:
                # no INTEL nodes are available change to AMD
                self.node_number_list = AMD_OPTERON_PROCESSOE_6376
                #new call to get new AMD node list
                my_busy_node_number = self.__get_free_node_number_list()
                if not my_busy_node_number:
                    # no INTEL and AMD nodes are available change to INTEL and wait
                    self.node_number_list = INTEL_XEON_CPU_E5_2683_V4
                    # new call to get new INTEL node list
                    my_busy_node_number = self.__get_free_node_number_list()
                    while not my_busy_node_number:
                        print("All nodes are occupide.")
                        time.sleep(30)
                        my_busy_node_number = self.__get_free_node_number_list()

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

    @staticmethod
    def rewrite_output_file(file_path, loops_list):
        f = open(file_path, "w")
        for loop in loops_list:
            f.write(f'run time of loop {loop[0]}: {loop[1]}\n')
        f.close()

    def add_nodelist_flag_into_slurm(self, user_slurm_parameters):

        if not ExecuteJob.has_nodelist_flag_in_slurm_parameters(user_slurm_parameters):
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
            ExecuteJob.MY_BUSY_NODE_NUMBER_LIST.append(node_number)
            return new_slurm_parameters
        return user_slurm_parameters.copy()

    def save_successful_job(self):
        self.update_speedup()
        job_result_dict = self.job.get_job_results()
        self.db_lock.acquire()
        self.db.insert_new_combination(job_result_dict)
        self.db_lock.release()

    def save_combination_as_failure(self, error_msg):
        combination_dict = {
            '_id': self.job.combination.combination_id,
            'error': error_msg
        }
        self.db_lock.acquire()
        self.db.insert_new_combination(combination_dict)
        self.db_lock.release()

    def update_speedup(self):
        job_results = self.job.get_job_results()['run_time_results']
        for file_dict in job_results:
            if 'dead_code_file' not in file_dict.keys():
                for loop_dict in file_dict['loops']:
                    try:
                        if not self.serial_run_time_dict:  # it is serial running
                            loop_dict['speedup'] = 1.0
                        elif 'dead_code' not in loop_dict.keys():
                            serial_run_time_key = (file_dict['file_id_by_rel_path'], loop_dict['loop_label'])
                            serial_run_time = float(self.serial_run_time_dict[serial_run_time_key])
                            parallel_run_time = float(loop_dict['run_time'])
                            try:
                                loop_dict['speedup'] = serial_run_time / parallel_run_time
                            except ZeroDivisionError:
                                loop_dict['speedup'] = 0.0

                    except KeyError as e:  # if one of the keys doesn't exists, just for debug.
                        error_msg = 'key error: ' + str(e) + f', in file {file_dict["file_id_by_rel_path"]}'
                        if 'missing_data' in file_dict.keys():
                            error_msg = file_dict['missing_data'] + f'\n{error_msg}'
                        file_dict['missing_data'] = error_msg

    def run(self, user_slurm_parameters):
        try:
            self.__run_with_sbatch(user_slurm_parameters)
            self.__analysis_output_file()
            self.update_dead_code_files()
            if self.save_results:
                self.save_successful_job()
        except Exception as ex:
            if self.job.get_job_results()['run_time_results']:
                self.save_successful_job()
            else:
                self.save_combination_as_failure(str(ex))

    def update_dead_code_files(self):
        job_results = self.job.get_job_results()['run_time_results']
        results_file_ids = [file_dict['file_id_by_rel_path'] for file_dict in job_results]
        for file_dict in self.relative_c_file_list:
            file_id = file_dict['file_relative_path']
            if file_id not in results_file_ids:
                job_results.append({'file_id_by_rel_path': file_id, 'dead_code_file': True})

    def __run_with_sbatch(self, user_slurm_parameters):
        # slurm_parameters = self.add_nodelist_flag_into_slurm(user_slurm_parameters)
        slurm_parameters = user_slurm_parameters
        dir_path = self.get_job().get_directory_path()
        dir_name = os.path.basename(dir_path)
        x_file = dir_name + ".x"
        sbatch_script_file = self.__make_sbatch_script_file(x_file)

        log_file = dir_name + ".log"
        x_file_path = os.path.join(dir_path, x_file)
        log_file_path = os.path.join(dir_path, log_file)
        slurm_parameters = " ".join(slurm_parameters)
        cmd = 'module load intel && sbatch {0} -o {1} {2} {3} {4} ' \
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

        if ExecuteJob.MY_BUSY_NODE_NUMBER_LIST:
            ExecuteJob.MY_BUSY_NODE_NUMBER_LIST.remove(self.get_run_node_number())

    def __make_sbatch_script_file(self, job_name=''):
        batch_file_path = os.path.join(self.get_job().get_directory_path(), 'batch_job.sh')
        batch_file = open(batch_file_path, 'w')
        batch_file.write(
            '#!/bin/bash\n'
            + f'#SBATCH --job-name={job_name}\n'
            + '#SBATCH --partition=grid\n'
            + '#SBATCH --exclusive\n'
            + '$@\n'
        )
        batch_file.close()
        return batch_file_path

    def __analysis_output_file(self):
        last_string = 'loop '
        for root, dirs, files in os.walk(self.get_job().get_directory_path()):
            for file in files:
                if re.search("_run_time_result.txt$", file):
                    loops_dict = {}
                    file_full_path = os.path.join(root, file)
                    file_id_by_rel_path = os.path.relpath(file_full_path, self.job.directory)
                    file_id_by_rel_path = file_id_by_rel_path.replace("_run_time_result.txt", ".c")
                    self.get_job().set_file_results(file_id_by_rel_path)
                    try:
                        with open(file_full_path, 'r') as input_file:
                            for line in input_file:
                                if ":" in line:
                                    line = line[line.find(last_string) +
                                                len(last_string)::].replace('\n', '').split(':')
                                    loop_label = line[0]
                                    loop_runtime = float(line[1])
                                    if loop_label not in loops_dict.keys():
                                        loops_dict[loop_label] = [loop_runtime]
                                    else:
                                        loops_dict[loop_label].append(loop_runtime)
                        loops_list = list(map(lambda x: (x[0], float(sum(x[1]))),
                                              loops_dict.items()))
                        ran_loops = [x[0] for x in loops_list]
                        for i in range(1, self.num_of_loops_in_files[file_id_by_rel_path][0] + 1):
                            if str(i) not in ran_loops:
                                self.get_job().set_loop_in_file_results(file_id_by_rel_path, i, None, dead_code=True)
                        for loop in loops_list:
                            self.get_job().set_loop_in_file_results(file_id_by_rel_path, loop[0], loop[1])
                        ExecuteJob.rewrite_output_file(file_full_path, loops_list)

                    except OSError as e:
                        raise FileError(str(e))
