import subprocess
from exceptions import FileError
from subprocess_handler import run_subprocess
import logger


def format_c_code(c_files_path_list, style_arguments='\"{AccessModifierOffset: -4, IndentWidth: 4}\"'):
    try:
        format_command = ['clang-format', '-i'] + c_files_path_list + ['-style', style_arguments]
        stdout, stderr, ret_code = run_subprocess(format_command)
        logger.info(stdout)
    except subprocess.CalledProcessError as e:
        raise FileError(f'Format Code Error: clang-format return with {e.returncode} code: {e.output}')
    except FileNotFoundError as e:
        raise FileError(e)
