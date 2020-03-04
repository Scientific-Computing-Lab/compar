from threading import Lock
import execute_job

from concurrent.futures import ThreadPoolExecutor


class Executor:

    @staticmethod
    def execute_jobs(jobs, num_of_loops_in_files, db, number_of_threads=1, slurm_parameters=None, save_results=True):
        if not slurm_parameters:
            slurm_parameters = []
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        db_lock = Lock()
        for job in jobs:
            pool.submit(execute_job.ExecuteJob(job, num_of_loops_in_files, db, db_lock, save_results).run, slurm_parameters)
        pool.shutdown()
        return jobs
