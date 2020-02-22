import os


class FileError(Exception):
    pass


class CompilationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class UserInputError(Exception):
    pass


class FolderError(Exception):
    pass


class DatabaseError(Exception):
    pass


class CombinationFailure(Exception):
    pass


class MissingDataError(Exception):
    pass


class MakefileError(Exception):
    pass


class FragmentError(Exception):
    pass


def assert_file_exist(file_path):
    if not os.path.exists(file_path):
        raise FileError('File {} not exist'.format(file_path))


def assert_file_from_format(file_path, _format):
    if not os.path.basename(file_path).split('.')[1].endswith(_format):
        raise FileError('File {0} should be in {1} format'.format(file_path, _format))


def assert_file_is_empty(file):
    if not file:
        raise FileError('File {0} is empty'.format(file))


def assert_only_files(folder_path):
    folder_content = os.listdir(folder_path)
    if len(folder_content) != len(list(filter(os.path.isfile, folder_content))):
        raise UserInputError('Input dir must contain only files!')


def assert_rel_path_starts_without_sep(path):
    if path.startswith(os.sep):
        raise UserInputError('Relative path should not start with separator!')
