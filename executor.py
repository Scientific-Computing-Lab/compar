import execute_job
from concurrent.futures import ThreadPoolExecutor


class Executor:

    @staticmethod
    def execute_jobs(jobs, number_of_threads=1):
        pool = ThreadPoolExecutor(max_workers=number_of_threads)
        for job in jobs():
            pool.submit(execute_job.Execute_job(job).run)
        pool.shutdown()
        return jobs
