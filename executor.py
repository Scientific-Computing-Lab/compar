import execute_job
import os

from concurrent.futures import ThreadPoolExecutor


class Executor:

    @staticmethod
    def execute_jobs(jobs, number_of_threads=1, slurm_parameters=None):
        if not slurm_parameters:
            slurm_parameters = []
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        for job in jobs:
            pool.submit(execute_job.Execute_job(job).run, slurm_parameters)
        pool.shutdown()
        return jobs
