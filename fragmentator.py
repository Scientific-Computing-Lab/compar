import re
import os
import shutil
from exceptions import FileError
from exceptions import assert_file_exist


class Fragmentator:
    __START_LOOP_LABEL_MARKER = '// START_LOOP_MARKER'
    __END_LOOP_LABEL_MARKER = '// END_LOOP_MARKER'

    @staticmethod
    def set_start_label(new_start_label):
        Fragmentator.__START_LOOP_LABEL_MARKER = new_start_label

    @staticmethod
    def set_end_label(new_end_label):
        Fragmentator.__END_LOOP_LABEL_MARKER = new_end_label

    def __init__(self, file_path):
        assert_file_exist(file_path)
        self.__file_path = file_path
        self.__file_content = ''
        self.__fragments = []

    def get_file_path(self):
        return self.__file_path

    def set_file_path(self, new_file_path):
        assert_file_exist(new_file_path)
        self.__file_path = new_file_path
        self.__file_content = ''
        self.__fragments = []

    def get_fragments(self):
        return self.__fragments

    def __backup_file(self):
        new_extension = '.old'
        try:
            shutil.copy(self.__file_path, self.__file_path + new_extension)
        except OSError as e:
            raise FileError(str(e))

    def __get_file_content(self):
        try:
            with open(self.__file_path, 'r') as input_file:
                self.__file_content = input_file.read()
        except FileNotFoundError:
            raise FileError('File {} not exist'.format(self.__file_path))
        if not self.__file_content:
            raise FileError('The file {} is empty'.format(self.__file_path))

    def __find_loops(self):
        for_loop_with_brackets = r'for[ \n\t\r]*\([^;]*;[^;]*;[^)]*\)[ \n\t\r]*\{([^;]*;)*[ \n\t\r]*\}'
        for_loop_without_brackets = r'for[ \n\t\r]*\([^;]*;[^;]*;[^)]*\)[^;]*;'
        for_loop_regex = re.compile(fr'{for_loop_with_brackets}|{for_loop_without_brackets}', re.DOTALL)
        loops = for_loop_regex.findall(self.__file_content)
        return list(set(loops))

    def __write_to_file(self, content):
        try:
            with open(self.__file_path, 'w') as output_file:
                output_file.write(content)
        except OSError as e:
            raise FileError(str(e))

    def __create_list_of_fragments(self):
        for index, loop in enumerate(self.__fragments, 1):
            loop_with_markers = {
                'start_label': self.__START_LOOP_LABEL_MARKER + str(index),
                'loop': loop,
                'end_label': self.__END_LOOP_LABEL_MARKER + str(index)
            }
            self.__fragments.append(loop_with_markers)

    def fragment_code(self):
        self.__backup_file()
        self.__get_file_content()
        self.__find_loops()
        self.__create_list_of_fragments()
        for loop_dict in self.__fragments:
            loop_with_markers = '\n' + loop_dict['start_label']
            loop_with_markers += loop_dict['loop']
            loop_with_markers += '\n' + loop_dict['end_label']
            self.__file_content = self.__file_content.replace(loop_dict['loop'], loop_with_markers)
        self.__write_to_file(self.__file_content)
        return self.get_fragments()
