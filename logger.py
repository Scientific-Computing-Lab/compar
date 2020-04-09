import traceback
import sys

REGULAR = 1
VERBOSE = 2
_log_level = REGULAR


def initialize(log_level):
    global _log_level
    _log_level = log_level


def info(message):
    print(message)


def debug(message):
    if _log_level == VERBOSE:
        print(message)


def info_error(message):
    print(message, file=sys.stderr)


def debug_error(message):
    if _log_level == VERBOSE:
        print(message, file=sys.stderr)


def log_to_file(message, file_path):
    try:
        with open(file_path, 'w') as log_file:
            log_file.write(message)
    except Exception as e:
        info_error(f'Logger cannot write to {file_path}: {e}')
        debug_error(f'{traceback.format_exc()}')
