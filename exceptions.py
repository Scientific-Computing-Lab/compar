import os


class FileError(Exception):
    pass


class CompilationError(Exception):
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


def assert_file_exist(file_path):
    if not os.path.exists(file_path):
        raise FileError('File {} not exist'.format(file_path))


def assert_file_from_format(file_path, _format):
    if not os.path.basename(file_path).split('.')[1].endswith(_format):
        raise FileError('File {0} should be in {1} format'.format(file_path, _format))


def assert_file_is_empty(file):
    if not file:
        raise FileError('File {0} is empty'.format(file))
