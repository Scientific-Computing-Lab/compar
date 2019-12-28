import os


class FileError(Exception):
    pass


def assert_file_exist(file_path):
    if not os.path.exists(file_path):
        raise FileError('File {} not exist'.format(file_path))


def assert_file_end_with_txt(file_path):
    if os.path.basename(file_path).split('.')[1] != 'txt':
        raise FileError('File {} should be in txt format'.format(file_path))
