import os

class Job:
    """
    * parameters :
    job_id - Contain the jod id that come from SCLUM
    directory - Contain the path to the directory the contains tha files of the job
    args - Contain all the arguments of the executable file
    combination - list of the combination that make the the job
    sections_runtime - a dictionary that contains all loops in the source file and the time that took him

    Data structures of combination: {combination_id:1234 ,



    Data structures of job_data: {'combination_id' : "1234" ,
                                          'run_time_result': [ { 'file_name' : "1234.C" ,
                                                                 'loops' : [ { 'loop_label' : "#123"
                                                                               'run_time' : "20"
                                                                               'speedup' : "1.25"
                                                                             } , ... , {...}
                                                                           ]
                                                               } , ... , {...}
                                                             ]
                                         }
    """


    #combination=None!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def __init__(self, directory, exec_file_args="", combination=None, ):
        self.directory = os.path.abspath(directory)
        self.exec_file_args = exec_file_args
        self.combination = combination
        self.job_id = ""
        self.log_file = ""
        self.job_results = {
            'job_id': self.get_job_id(),
            'combination_id': str(self.get_combination().get_id()),
            'run_time_result': []
        }

    def set_job_id(self, job_id):
        self.job_id = job_id
        self.job_results["job_id"] = str(job_id)
        return self.job_id

    def get_job_id(self):
        return self.job_id

    def set_directory_path(self, new_path):
        self.directory = os.path.abspath(new_path)

    def get_directory_path(self):
        return os.path.abspath(self.directory)

    def get_directory_name(self):
        return os.path.basename(self.directory)

    def set_exec_file_args(self, args):
        self.exec_file_args = args

    def get_exec_file_args(self):
        return self.exec_file_args

    def set_combination(self, combination):
        self.combination = combination

    def get_combination(self):
        return self.combination

    def set_job_results(self, job_id, combination_id, run_time_result):
        self.job_results = {
            'job_id': str(job_id),
            'combination_id': str(combination_id),
            'run_time_result': run_time_result}

    def get_job_results(self):
        return self.job_results

    def set_file_results(self, file_name, loops):
        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:
                file['loops'] = loops
                return
        self.job_results['run_time_result'].append({'file_name': file_name, 'loops': []})

    def get_file_results(self, file_name):
        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:
                return file
        raise Exception("File name: " + str(file_name) + " does not exist.")

    def set_file_results_loops(self, file_name, loops):

        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:
                file['loops'] = loops
                return

        raise Exception("File name: " + str(file_name) + " does not exist.")

    def set_loop_in_file_results(self, file_name, loop_label, run_time, speedup):

        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:

                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        loop["run_time"] = str(run_time)
                        loop["speedup"] = str(speedup)
                        return

                file['loops'].append({"loop_label": str(loop_label),
                                      "run_time": str(run_time),
                                      "speedup": str(speedup)})
                return

        raise Exception("File name: " + str(file_name) + " does not exist.")

    def set_loop_speedup_in_file_results(self, file_name, loop_label, speedup):
        file_or_loop_lable_dose_not_exist_flag = True

        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        loop["speedup"] = str(speedup)
                        file_or_loop_lable_dose_not_exist_flag = False

                if file_or_loop_lable_dose_not_exist_flag:
                    raise Exception("Loop label: " + str(loop_label) + " does not exist.")

        if file_or_loop_lable_dose_not_exist_flag:
            raise Exception("File name: " + str(file_name) + " does not exist.")

    def set_loop_run_time_in_file_results(self, file_name, loop_label, run_time):
        file_or_loop_lable_dose_not_exist_flag = True

        for file in self.job_results['run_time_result']:
            if file['file_name'] == file_name:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        loop["speedup"] = str(run_time)
                        file_or_loop_lable_dose_not_exist_flag = False

                if file_or_loop_lable_dose_not_exist_flag:
                    raise Exception("Loop label: " + str(loop_label) + " does not exist.")

        if file_or_loop_lable_dose_not_exist_flag:
            raise Exception("File name: " + str(file_name) + " does not exist.")


