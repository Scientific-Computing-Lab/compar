import os


class FileError(Exception):
    pass


def assert_file_exist(file_path):
    if not os.path.exists(file_path):
        raise FileError('File {} not exist'.format(file_path))
