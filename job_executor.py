from threading import RLock
from concurrent.futures import ThreadPoolExecutor


class JobExecutor:

    def __init__(self, number_of_threads=1):
        self.number_of_threads = number_of_threads
        self.db_lock = RLock()
        self.pool = None

    def create_jobs_pool(self):
        self.pool = ThreadPoolExecutor(max_workers=self.number_of_threads, thread_name_prefix='compar_job_thread')

    def get_db_lock(self):
        return self.db_lock

    def run_job_in_thread(self, func, job):
        self.pool.submit(func, job)

    def wait_and_finish_pool(self):
        self.pool.shutdown()
        self.pool = None
