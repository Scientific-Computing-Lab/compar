import subprocess
from exceptions import FileError
from subprocess_handler import run_subprocess
import re
from globals import FileFormatorConfig


def format_c_code(c_files_path_list, column_limit=True):
    style_arguments = ', '.join(FileFormatorConfig.STYLE_ARGUMENTS)
    if column_limit:
        style_arguments += f', {FileFormatorConfig.COLUMN_LIMIT_STYLE_ARGUMENT}'
    style_arguments = f'\"{{{style_arguments}}}\"'
    try:
        format_command = ['source',  'scl_source', 'enable',  'llvm-toolset-7', '&&']
        format_command += ['clang-format', '-i'] + c_files_path_list + ['-style', style_arguments]

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
        new_lines.append(re.sub(r'^[ \t]*#', f'{FileFormatorConfig.COMMENT_PREFIX}#', line))
    return '\n'.join(new_lines)


def uncomment_directives(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(re.sub(rf'{FileFormatorConfig.COMMENT_PREFIX}#', '#', line))
    return '\n'.join(new_lines)


