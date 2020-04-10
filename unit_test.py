import enum
import os
import pytest
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


class UnitTest:
    UNIT_TEST_FILE_NAME = 'test_output.py'
    UNIT_TEST_DEFAULT_PATH = os.path.join('assets', UNIT_TEST_FILE_NAME)
    UNIT_TEST_NAME = 'test_output'

    @staticmethod
    def run_unit_test(test_file_path):
        exit_code = ""
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            exit_code = pytest.main(["-q", f"{test_file_path}::{UnitTest.UNIT_TEST_NAME}"])
        return exit_code == ExitCode.OK

    @staticmethod
    def check_if_test_exists(test_file_path):
        exit_code = ""
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            exit_code = pytest.main(["-q", f"{test_file_path}::{UnitTest.UNIT_TEST_NAME}"])
        return exit_code not in [ExitCode.NO_TESTS_COLLECTED, ExitCode.USAGE_ERROR]


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
