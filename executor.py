from threading import Lock
import execute_job

from concurrent.futures import ThreadPoolExecutor


class Executor:

    @staticmethod
    def execute_jobs(jobs, num_of_loops_in_files, db, relative_c_file_list, slurm_partition, test_file_path,
                     number_of_threads=1, slurm_parameters=None, serial_run_time=None, time_limit=None):
        if not slurm_parameters:
            slurm_parameters = []
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        db_lock = Lock()
        for job in jobs:
            pool.submit(execute_job.ExecuteJob(job, num_of_loops_in_files, db, db_lock, serial_run_time,
                                               relative_c_file_list, slurm_partition, test_file_path,
                                               time_limit).run, slurm_parameters)
        pool.shutdown()
        return jobs
