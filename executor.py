import execute_job
import os

from concurrent.futures import ThreadPoolExecutor


class Executor:

    @staticmethod
    def execute_jobs(jobs, number_of_threads=1):
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        for job in jobs():
            log_file = open(os.path.join(job.get_directory_path(), job.get_directory_name()+'.log'), 'a')
            pool.submit(execute_job.Execute_job(job, log_file).run)
        pool.shutdown()
        return jobs
