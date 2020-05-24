import re
from exceptions import FileError
from exceptions import assert_file_exist
from exceptions import FragmentError
from exceptions import UserInputError
from file_formator import format_c_code
from globals import FragmentatorConfig


class Fragmentator:
    __START_LOOP_LABEL_MARKER = FragmentatorConfig.START_LOOP_LABEL_MARKER
    __END_LOOP_LABEL_MARKER = FragmentatorConfig.END_LOOP_LABEL_MARKER

    @staticmethod
    def set_start_label(new_start_label: str):
        Fragmentator.__START_LOOP_LABEL_MARKER = new_start_label

    @staticmethod
    def set_end_label(new_end_label: str):
        Fragmentator.__END_LOOP_LABEL_MARKER = new_end_label

    @staticmethod
    def get_start_label():
        return Fragmentator.__START_LOOP_LABEL_MARKER

    @staticmethod
    def get_end_label():
        return Fragmentator.__END_LOOP_LABEL_MARKER

    @staticmethod
    def count_loops_in_prepared_file(file_path: str):
        with open(file_path, 'r') as fp:
            content = fp.read()
        all_markers = re.findall(rf'.*{FragmentatorConfig.LOOP_LABEL_MARKER}\d+', content)
        loop_labels = list(set([int(re.search(r'\d+$', marker).group(0)) for marker in all_markers if marker]))
        try:
            num_of_loops = max(loop_labels)
        except ValueError:  # in case of max on empty list
            num_of_loops = 0
        if num_of_loops != len(loop_labels):
            raise UserInputError(f'Error in {file_path}: the file must contains #{num_of_loops} loop markers!')
        return num_of_loops

    def __init__(self, file_path: str, code_with_markers: bool = False):
        assert_file_exist(file_path)
        self.__file_path = file_path
        self.__file_content = ''
        self.__loops_list = []
        self.__fragments = []
        self.__occurrences_index_list = []
        self.code_with_markers = code_with_markers

    def __reset_data(self):
        self.__file_content = ''
        self.__loops_list.clear()
        self.__fragments.clear()
        self.__occurrences_index_list.clear()

    def get_file_path(self):
        return self.__file_path

    def set_file_path(self, new_file_path: str):
        assert_file_exist(new_file_path)
        self.__file_path = new_file_path
        self.__reset_data()

    def get_fragments(self):
        return self.__fragments

    def __get_file_content(self):
        format_c_code([self.__file_path, ], column_limit=False)
        try:
            with open(self.__file_path, 'r') as input_file:
                self.__file_content = input_file.read()
        except FileNotFoundError:
            raise FileError(f'File {self.__file_path} dose not exist')
        if not self.__file_content:
            raise FileError(f'The file {self.__file_path} is empty')

    def __find_loops(self):
        lines = self.__file_content.split('\n')
        self.__occurrences_index_list = []

        current_loop = {
            'start_position_index': -1,
            'loop_lines': [],
            'with_brackets': True
        }
        found_start = False
        found_while = {}

        def save_and_reset_data_to_new_loop():
            nonlocal found_start
            loop = '\n'.join(current_loop['loop_lines'])
            current_occurrence_index = 1
            if loop in self.__loops_list:
                current_occurrence_index = self.__loops_list.count(loop) + 1
            self.__loops_list.append(loop)
            self.__occurrences_index_list.append(current_occurrence_index)
            found_start = False
            current_loop['start_position_index'] = -1
            current_loop['loop_lines'].clear()
            current_loop['with_brackets'] = True

        for line in lines:
            if not line:
                if found_start:
                    current_loop['loop_lines'].append('')
                continue
            if found_start:
                indent_chars = line[:current_loop['start_position_index']]
                try:
                    first_char_after_indent = line[current_loop['start_position_index']]
                    is_indent_only_spaces = indent_chars == '' or set(indent_chars) == set(' ')
                    if is_indent_only_spaces and len(indent_chars) == current_loop['start_position_index']:
                        if first_char_after_indent == ' ':
                            current_loop['loop_lines'].append(line)
                        else:
                            if current_loop['with_brackets'] and first_char_after_indent == '}':
                                current_loop['loop_lines'].append(line)
                            save_and_reset_data_to_new_loop()
                    else:
                        save_and_reset_data_to_new_loop()
                except IndexError:
                    # the line is shorter than the required indent, the loop is ended.
                    # the current line may be a new loop
                    save_and_reset_data_to_new_loop()
            if not found_start:  # NOTICE THE COMMENT BELOW!!!
                # it is not the opposite of "if found_start"!!!!
                # because the "found_start" flag can be changed during the above if statement

                if found_while:
                    if found_while['with_brackets']:
                        try:
                            prefix_only_spaces = set(line[:found_while['line_offset']]) == set(' ')
                            if prefix_only_spaces and line[found_while['line_offset']] == '}':
                                found_while.clear()
                        except IndexError:
                            raise FragmentError(
                                'Close bracket } of while loop is missing! (Maybe you forgot to run clang-format?)')
                    else:  # that line is the body of the loop, there is only one line
                        prefix_last_space_position = re.search(r'^[ ]+', line).end()
                        is_not_comment_or_pragma = not re.search(r'^//|^#|^/\*', line)
                        start_with_same_offset = prefix_last_space_position <= found_while['line_offset']
                        if is_not_comment_or_pragma and line != '' and start_with_same_offset:
                            found_while.clear()
                if not found_while:  # NOTICE THE COMMENT BELOW!!!
                    # it is not the opposite of "if found_while"!!!!
                    # because the "found_while" flag can be changed during the above if statement

                    for_loop_regex_result = re.search('^[ ]*for', line)
                    while_loop_regex_result = re.search('^[ ]*while', line)
                    end_with_bracket_pattern = r'{[ ]*$|{[ ]*//[\w\W]*$|{[ ]*/\*[\w\W]*$'
                    if while_loop_regex_result:
                        found_while['line_offset'] = re.search('while', line).start()
                        with_bracket = re.search(end_with_bracket_pattern, line)
                        found_while['with_brackets'] = with_bracket is not None
                    elif for_loop_regex_result and not found_while:
                        found_start = True
                        current_loop['loop_lines'].append(line)
                        current_loop['start_position_index'] = re.search('for', for_loop_regex_result.string).start()
                        if not re.search(end_with_bracket_pattern, line):
                            current_loop['with_brackets'] = False

    def __write_to_file(self, content: str):
        try:
            with open(self.__file_path, 'w') as output_file:
                output_file.write(content)
        except OSError as e:
            raise FileError(str(e))

    def __create_list_of_fragments(self):
        for index, loop in enumerate(self.__loops_list, 1):
            loop_with_markers = {
                'start_label': self.__START_LOOP_LABEL_MARKER + str(index),
                'loop': loop,
                'end_label': self.__END_LOOP_LABEL_MARKER + str(index)
            }
            self.__fragments.append(loop_with_markers)

    def remove_spaces_before_marker(self):
        regex_start = re.compile(rf'[ \t]*{self.__START_LOOP_LABEL_MARKER}')
        regex_end = re.compile(rf'[ \t]*{self.__END_LOOP_LABEL_MARKER}')
        self.__file_content = regex_start.sub(f'{self.__START_LOOP_LABEL_MARKER}', self.__file_content)
        self.__file_content = regex_end.sub(f'{self.__END_LOOP_LABEL_MARKER}', self.__file_content)
        self.__write_to_file(self.__file_content)

    def __search_markers(self):
        self.remove_spaces_before_marker()
        regex = re.compile(rf'{FragmentatorConfig.START_MARKER}(?P<loop_id>\d+).*'
                           rf'{FragmentatorConfig.END_MARKER}(?P=loop_id)[ ]*\n', re.DOTALL)
        loops_with_markers = [loop.group() for loop in regex.finditer(self.__file_content)]
        start_marker_pattern = rf'{FragmentatorConfig.START_MARKER}\d+'
        end_marker_pattern = rf'{FragmentatorConfig.END_MARKER}\d+'
        for loop in loops_with_markers:
            start_marker = f'// {re.search(start_marker_pattern, loop).group()}'
            end_marker = f'// {re.search(end_marker_pattern, loop).group()}'
            just_loop = re.sub(rf'{start_marker_pattern}[^\n]*\n', '', loop)
            just_loop = re.sub(rf'\n.+{end_marker_pattern}[ ]*\n', '', just_loop)
            loop_and_markers = {
                'start_label': start_marker,
                'loop': just_loop,
                'end_label': end_marker
            }
            self.__fragments.append(loop_and_markers)
        try:
            num_of_loops = max([int(re.search(r'\d+', loop['start_label']).group()) for loop in self.__fragments])
        except ValueError:  # in case of max on empty list
            num_of_loops = 0
        if num_of_loops != len(loops_with_markers):
            raise UserInputError(f'Error in {self.__file_path}: the file must contains #{num_of_loops} loop markers!')
        return self.__fragments

    def move_omp_directives_into_marker(self):
        for i, loop_fragment in enumerate(self.__fragments, 1):
            pragma_pattern = rf'[\t ]*#pragma omp[^\n]+\n(?=[\n\t ]*{self.__START_LOOP_LABEL_MARKER}{i}[ \t]*\n)'
            pragma = re.search(pragma_pattern, self.__file_content)
            if pragma:
                pragma = pragma.group()
                self.__file_content = re.sub(rf'{pragma_pattern}[\n\t ]*{self.__START_LOOP_LABEL_MARKER}{i}[ \t]*\n',
                                             f'{self.__START_LOOP_LABEL_MARKER}{i}\n{pragma}', self.__file_content)
                loop_fragment['loop'] = f'{pragma}{loop_fragment["loop"]}'
        self.__write_to_file(self.__file_content)

    def drop_markers_inside_comments(self):
        # remove markers inside  multi-lines comments
        all_comments = re.findall(r'/\*.*?\*/', self.__file_content, re.DOTALL)
        start_marker_pattern = rf'[ \t]*{FragmentatorConfig.START_LOOP_LABEL_MARKER}\d+\n'
        end_marker_pattern = rf'[ \t]*{FragmentatorConfig.END_LOOP_LABEL_MARKER}\d+\n'
        for comment in all_comments:
            new_comment = re.sub(start_marker_pattern, '', comment)
            new_comment = re.sub(end_marker_pattern, '', new_comment)
            self.__file_content = self.__file_content.replace(comment, new_comment)
        # count again the loops (the loop ids was changed because of the above removal)
        all_start_markers = re.findall(start_marker_pattern, self.__file_content)
        all_end_markers = re.findall(end_marker_pattern, self.__file_content)
        if len(all_start_markers) != len(all_end_markers):
            raise FragmentError('The amount of start loop markers and end loop markers is not the same')
        new_amount_of_markers = len(all_start_markers)
        if new_amount_of_markers == 0:
            return
        for marker_index in range(new_amount_of_markers):
            new_start_marker = f'{FragmentatorConfig.START_LOOP_LABEL_MARKER}{marker_index + 1}\n'
            new_end_marker = f'{FragmentatorConfig.END_LOOP_LABEL_MARKER}{marker_index + 1}\n'
            self.__file_content = self.__file_content.replace(all_start_markers[marker_index], new_start_marker)
            self.__file_content = self.__file_content.replace(all_end_markers[marker_index], new_end_marker)
        # update self.__fragments list
        self.__fragments = []
        for loop_id in range(1, new_amount_of_markers + 1):
            start_label = f'{FragmentatorConfig.START_LOOP_LABEL_MARKER}{loop_id}'
            end_label = f'{FragmentatorConfig.END_LOOP_LABEL_MARKER}{loop_id}'
            pattern = rf'{start_label}\n.*?\n{end_label}'
            loop_with_markers = re.search(pattern, self.__file_content, re.DOTALL).group()
            loop_fragment = {
                'start_label': start_label,
                'loop': loop_with_markers.replace(f'{start_label}\n', '').replace(f'\n{end_label}', ''),
                'end_label': end_label
            }
            self.__fragments.append(loop_fragment)

    def fragment_code(self):
        self.__get_file_content()
        if self.code_with_markers:
            return self.__search_markers()
        self.__find_loops()
        self.__create_list_of_fragments()
        new_content = ''
        rest_of_the_content = self.__file_content
        for i, loop_fragment in enumerate(self.__fragments):
            loop_start_offset = rest_of_the_content.find(loop_fragment['loop'])
            if loop_start_offset == -1:
                raise FragmentError(f'Cannot find loop {loop_fragment["loop"]}')
            loop_end_offset = loop_start_offset + len(loop_fragment['loop'])
            loop_with_markers = loop_fragment['start_label'] + '\n'
            loop_with_markers += loop_fragment['loop']
            loop_with_markers += '\n' + loop_fragment['end_label']
            new_content += rest_of_the_content[:loop_start_offset]
            new_content += loop_with_markers
            rest_of_the_content = rest_of_the_content[loop_end_offset:]
        new_content += rest_of_the_content
        self.__file_content = new_content
        self.drop_markers_inside_comments()
        self.__write_to_file(self.__file_content)
        if not self.code_with_markers:
            self.move_omp_directives_into_marker()
        return self.get_fragments()
