import subprocess
from exceptions import FileError


def format_c_code(c_files_path_list, style_arguments='{AccessModifierOffset: -4, IndentWidth: 4}'):
    try:
        format_command = ['clang-format', '-i'] + c_files_path_list + ['-style', style_arguments]
        output = subprocess.check_output(format_command)
    except subprocess.CalledProcessError as e:
        raise FileError(f'Format Code Error: clang-format return with {e.returncode} code: {e.output}')
    except FileNotFoundError as e:
        raise FileError(e)
