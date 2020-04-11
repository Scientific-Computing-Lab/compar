from threading import RLock
import traceback
import sys

NO_OUTPUT = 0
BASIC = 1
VERBOSE = 2
DEBUG = 3
_log_level = BASIC
print_lock = RLock()


def get_log_level():
    return _log_level


def initialize(log_level):
    global _log_level
    _log_level = log_level


def info(message):
    if _log_level != NO_OUTPUT:
        print_lock.acquire()
        print(message)
        print_lock.release()


def verbose(message):
    if _log_level in (VERBOSE, DEBUG):
        print_lock.acquire()
        print(message)
        print_lock.release()


def debug(message):
    if _log_level == DEBUG:
        print_lock.acquire()
        print(message)
        print_lock.release()


def info_error(message):
    if _log_level != NO_OUTPUT:
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def verbose_error(message):
    if _log_level in (VERBOSE, DEBUG):
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def debug_error(message):
    if _log_level == DEBUG:
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def log_to_file(message, file_path, append=False):
    mode = 'a' if append else 'w'
    try:
        print_lock.acquire()
        with open(file_path, mode) as log_file:
            log_file.write(message)
            if append:
                log_file.write('\n\n')
    except Exception as e:
        info_error(f'Logger cannot write to {file_path}: {e}')
        debug_error(f'{traceback.format_exc()}')
    finally:
        print_lock.release()
