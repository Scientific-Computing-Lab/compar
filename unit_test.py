import enum
import os
import pytest
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import logger


class UnitTest:
    UNIT_TEST_FILE_NAME = 'test_output.py'
    UNIT_TEST_DEFAULT_PATH = os.path.join('assets', UNIT_TEST_FILE_NAME)
    UNIT_TEST_NAME = 'test_output'

    @staticmethod
    def trigger_test_output_test(test_file_path, message=""):
        exit_code = None
        unit_test_stdout = StringIO()
        unit_test_stderr = StringIO()
        with redirect_stdout(unit_test_stdout), redirect_stderr(unit_test_stderr):
            command = [f"{test_file_path}::{UnitTest.UNIT_TEST_NAME}"]
            if logger.get_log_level() != logger.DEBUG:
                command += ['-q']
            exit_code = pytest.main(command)
        logger.verbose(f"{UnitTest.__name__}: {message}{unit_test_stdout.getvalue()}\n{unit_test_stderr.getvalue()}.")
        return exit_code

    @staticmethod
    def run_unit_test(test_file_path):
        return UnitTest.trigger_test_output_test(test_file_path) == ExitCode.OK

    @staticmethod
    def check_if_test_exists(test_file_path):
        message = f"Checking the existence of test: '{UnitTest.UNIT_TEST_NAME}'\n"
        return UnitTest.trigger_test_output_test(test_file_path, message) not in \
            [ExitCode.NO_TESTS_COLLECTED, ExitCode.USAGE_ERROR]


class ExitCode(enum.IntEnum):
    #: tests passed
    OK = 0
    #: tests failed
    TESTS_FAILED = 1
    #: pytest was interrupted
    INTERRUPTED = 2
    #: an internal error got in the way
    INTERNAL_ERROR = 3
    #: pytest was misused
    USAGE_ERROR = 4
    #: pytest couldn't find tests
    NO_TESTS_COLLECTED = 5
