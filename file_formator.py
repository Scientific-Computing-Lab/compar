import subprocess
from exceptions import FileError
from subprocess_handler import run_subprocess
import re

COMMENT_PREFIX = '//____compar____'


def format_c_code(c_files_path_list, column_limit=True):
    style_arguments = '\"{AccessModifierOffset: -4, IndentWidth: 4'
    if column_limit:
        style_arguments += ', ColumnLimit: 0'
    style_arguments += '}\"'
    try:
        format_command = ['clang-format', '-i'] + c_files_path_list + ['-style', style_arguments]
        run_subprocess(format_command)
        directives_handler(c_files_path_list)
        run_subprocess(format_command)
        directives_handler(c_files_path_list, back=True)
    except subprocess.CalledProcessError as e:
        raise FileError(f'Format Code Error: clang-format return with {e.returncode} code: {e.output}')
    except FileNotFoundError as e:
        raise FileError(e)


def directives_handler(file_paths_list, back=False):
    for file_path in file_paths_list:
        with open(file_path, 'r+') as fp:
            content = fp.read()
            if back:
                content = uncomment_directives(content)
            else:
                content = comment_directives(content)
            fp.seek(0)
            fp.write(content)
            fp.truncate()


def comment_directives(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(re.sub(r'^[ \t]*#', f'{COMMENT_PREFIX}#', line))
    return '\n'.join(new_lines)


def uncomment_directives(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(re.sub(rf'{COMMENT_PREFIX}#', '#', line))
    return '\n'.join(new_lines)


