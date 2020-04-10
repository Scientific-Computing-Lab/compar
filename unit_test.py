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
        return exit_code == pytest.ExitCode.OK

    @staticmethod
    def check_if_test_exists(test_file_path):
        exit_code = ""
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            exit_code = pytest.main(["-q", f"{test_file_path}::{UnitTest.UNIT_TEST_NAME}"])
        return exit_code not in [pytest.ExitCode.NO_TESTS_COLLECTED, pytest.ExitCode.USAGE_ERROR]
