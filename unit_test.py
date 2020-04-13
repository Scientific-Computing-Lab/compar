import enum
import os
from subprocess import CalledProcessError

from subprocess_handler import run_subprocess
import logger


class UnitTest:
    UNIT_TEST_FILE_NAME = 'test_output.py'
    UNIT_TEST_DEFAULT_PATH = os.path.join('assets', UNIT_TEST_FILE_NAME)
    UNIT_TEST_NAME = 'test_output'

    @staticmethod
    def trigger_test_output_test(test_file_path, working_dir="", output_file_name="", message=""):
        exit_code = None
        stdout = ""
        stderr = ""
        command = ["pytest"]
        command += [f"{test_file_path}::{UnitTest.UNIT_TEST_NAME}"]
        if working_dir:
            command += ["--working_dir", working_dir]
        if output_file_name:
            command += ["--output_file_name", output_file_name]
        command = " ".join(command)
        try:
            stdout, stderr, exit_code = run_subprocess(command)
        except CalledProcessError as e:
            if e.returncode is None or e.returncode not in [code for code in ExitCode]:
                logger.info_error(f"{UnitTest.__name__}: pytest operation failed. test failed.\n{e}")
                return ExitCode.INTERNAL_ERROR
            stdout = e.stdout
            stderr = e.stderr
            exit_code = e.returncode
        except Exception as ex:
            logger.info_error(f"{UnitTest.__name__}: exception thrown during pytest operation. test failed.\n{ex}")
            return ExitCode.INTERNAL_ERROR
        if exit_code == ExitCode.OK:
            logger.verbose(f"{UnitTest.__name__}: test '{UnitTest.UNIT_TEST_NAME}' passed.")
        else:
            logger.info_error(f"{UnitTest.__name__}: test '{UnitTest.UNIT_TEST_NAME}' failed.")
        logger.debug(f"{UnitTest.__name__}: {message}{stdout}\n{stderr}.")
        return exit_code

    @staticmethod
    def run_unit_test(test_file_path, working_dir="", output_file_name=""):
        return UnitTest.trigger_test_output_test(test_file_path, working_dir, output_file_name) == ExitCode.OK

    @staticmethod
    def check_if_test_exists(test_file_path):
        message = f"Checking the existence of test: '{UnitTest.UNIT_TEST_NAME}'\n"
        return UnitTest.trigger_test_output_test(test_file_path, message=message) not in \
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
