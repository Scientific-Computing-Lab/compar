import os


class Job:
    """
    * parameters :
    job_id - Contain the jod id that come from Slurm
    directory - Contain the path to the directory the contains tha files of the job
    exec_file_args - Contain all the arguments of the executable file
    combination - Object of the combination that make the the job
    job_results - a dictionary that contains all loops in the source file and the time that took him

    Data structures of job_results: {'_id' : "1234" ,
                                    'job_id':"1232132132",
                                    'total_run_time': 123,
                                    'run_time_results': [ { 'file_id_by_rel_path' : "/test1/1234.C" ,
                                                                 'loops' : [ { 'loop_label' : "#123"
                                                                               'run_time' : "20"
                                                                               'speedup' : "1.25"
                                                                             } , ... , {...}
                                                                           ]
                                                               } , ... , {...}
                                                             ]
                                         }
    """

    RUNTIME_ERROR = -1

    def __init__(self, directory, combination, exec_file_args=""):
        self.directory = directory
        self.exec_file_args = exec_file_args
        self.combination = combination
        self.job_id = ""
        self.total_run_time = 0
        self.log_file = ""
        self.job_results = {
            'job_id': self.get_job_id(),
            '_id': str(self.get_combination().get_combination_id()),
            'run_time_results': [],
            'total_run_time': Job.RUNTIME_ERROR
        }

    def set_job_id(self, job_id):
        self.job_id = job_id
        self.job_results["job_id"] = str(job_id)

    def get_job_id(self):
        return self.job_id

    def set_total_run_time(self, total_run_time):
        self.total_run_time = total_run_time
        self.job_results['total_run_time'] = total_run_time

    def get_total_run_time(self):
        return self.total_run_time

    def set_directory_path(self, new_path):
        self.directory = new_path

    def get_directory_path(self):
        return self.directory

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

    def set_job_results(self, job_id, combination_id, run_time_results):
        self.job_results = {
            'job_id': str(job_id),
            '_id': str(combination_id),
            'run_time_results': run_time_results}

    def get_job_results(self):
        return self.job_results

    def set_file_results(self, file_id_by_rel_path):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                file['loops'] = []
                return
        self.job_results['run_time_results'].append({'file_id_by_rel_path': file_id_by_rel_path, 'loops': []})

    def get_file_results(self, file_id_by_rel_path):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                return file
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def set_file_results_loops(self, file_id_by_rel_path, loops):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                file['loops'] = loops
                return
        self.job_results['run_time_results'].append({'file_id_by_rel_path': file_id_by_rel_path, 'loops': loops})

    def get_file_results_loops(self, file_id_by_rel_path):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                return file['loops']
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def set_loop_in_file_results(self, file_id_by_rel_path, loop_label, run_time, dead_code=False, speedup=0):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                if dead_code:
                    file['loops'].append({"loop_label": str(loop_label), "dead_code": True})
                    return
                else:
                    for loop in file['loops']:
                        if loop["loop_label"] == str(loop_label):
                            loop["run_time"] = run_time
                            loop["speedup"] = speedup
                            return
                    file['loops'].append({"loop_label": str(loop_label),
                                          "run_time": run_time,
                                          "speedup": speedup})
                return
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def get_loop_in_file_results(self, file_id_by_rel_path, loop_label):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        return loop
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def set_loop_speedup_in_file_results(self, file_id_by_rel_path, loop_label, speedup):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        loop["speedup"] = speedup
                        return
                raise Exception("Loop label: " + str(loop_label) + " does not exist.")
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def get_loop_speedup_in_file_results(self, file_id_by_rel_path, loop_label):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        return loop["speedup"]
                raise Exception("Loop label: " + str(loop_label) + " does not exist.")
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def set_loop_run_time_in_file_results(self, file_id_by_rel_path, loop_label, run_time):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        loop["run_time"] = run_time
                        return
                raise Exception("Loop label: " + str(loop_label) + " does not exist.")
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

    def get_loop_run_time_in_file_results(self, file_id_by_rel_path, loop_label):
        for file in self.job_results['run_time_results']:
            if file['file_id_by_rel_path'] == file_id_by_rel_path:
                for loop in file['loops']:
                    if loop["loop_label"] == str(loop_label):
                        return loop["run_time"]
                raise Exception("Loop label: " + str(loop_label) + " does not exist.")
        raise Exception("File in path: " + str(file_id_by_rel_path) + " does not exist.")

