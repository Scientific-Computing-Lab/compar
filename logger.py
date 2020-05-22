from threading import RLock
import logging
import traceback
import sys
import os

NO_OUTPUT = 0
BASIC = 1
VERBOSE = 2
DEBUG = 3
DEFAULT_LOG_LEVEL = BASIC
LOG_FILE_NAME = 'compar_output.log'
_log_level = DEFAULT_LOG_LEVEL
_output_folder_path = ''
print_lock = RLock()


def get_log_level():
    return _log_level


def initialize(log_level: int, output_folder_path: str):
    global _log_level, _output_folder_path
    _log_level = log_level
    if os.path.exists(output_folder_path):
        _output_folder_path = output_folder_path
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(threadName)s | %(message)s',
                        filename=os.path.join(_output_folder_path, LOG_FILE_NAME),
                        datefmt='%Y/%m/%d %H:%M:%S')
    logging.debug('-' * 50)


def info(message: str):
    logging.debug(message)
    if _log_level != NO_OUTPUT:
        print_lock.acquire()
        print(message)
        print_lock.release()


def verbose(message: str):
    logging.debug(message)
    if _log_level in (VERBOSE, DEBUG):
        print_lock.acquire()
        print(message)
        print_lock.release()


def debug(message: str):
    logging.debug(message)
    if _log_level == DEBUG:
        print_lock.acquire()
        print(message)
        print_lock.release()


def info_error(message: str):
    logging.debug(message)
    if _log_level != NO_OUTPUT:
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def verbose_error(message: str):
    logging.debug(message)
    if _log_level in (VERBOSE, DEBUG):
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def debug_error(message: str):
    logging.debug(message)
    if _log_level == DEBUG:
        print_lock.acquire()
        print(message, file=sys.stderr)
        print_lock.release()


def log_to_file(message: str, file_path: str, append: bool = False):
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
