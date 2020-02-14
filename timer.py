import os
from fragmentator import Fragmentator
import exceptions as e


class Timer(object):

    COMPAR_VAR_PREFIX = '____compar____'
    # WARNING! '__PREFIX_OUTPUT_FILE' var cannot contains semicolon!
    __PREFIX_OUTPUT_FILE = '#)$-@,(&=!+%^____,(&=__compar__@__should_+__be_+%___unique_(&!+$-=!+@%=!'
    DECL_START_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'start_time_{};\n'
    DECL_RUN_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'run_time_{};\n'
    DECL_FILE_POINTER_VAR_CODE = 'FILE *' + COMPAR_VAR_PREFIX + 'fp{};\n'
    INIT_START_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'start_time_{} = omp_get_wtime();\n'
    INIT_RUN_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'run_time_{} = omp_get_wtime() - ' +\
                             COMPAR_VAR_PREFIX + 'start_time_{};\n'
    WRITE_TO_FILE_CODE = COMPAR_VAR_PREFIX + 'fp{} = fopen(\"' + __PREFIX_OUTPUT_FILE + '{}\", \"a\");\n'
    WRITE_TO_FILE_CODE += 'fprintf(' + COMPAR_VAR_PREFIX + 'fp{}, \"run time of loop %d: %lf\\n\", {}, ' + \
                          COMPAR_VAR_PREFIX + 'run_time_{});\n'
    WRITE_TO_FILE_CODE += 'fclose(' + COMPAR_VAR_PREFIX + 'fp{});\n'

    @staticmethod
    def get_file_name_prefix_token():
        return Timer.__PREFIX_OUTPUT_FILE

    @staticmethod
    def get_declarations_code(label):
        declaration_code = '\n'
        declaration_code += Timer.DECL_START_TIME_VAR_CODE.format(label)
        declaration_code += Timer.DECL_RUN_TIME_VAR_CODE.format(label)
        declaration_code += Timer.DECL_FILE_POINTER_VAR_CODE.format(label)
        return declaration_code

    @staticmethod
    def get_prefix_loop_code(label):
        prefix_loop_code = '\n'
        prefix_loop_code += Timer.get_declarations_code(label)
        prefix_loop_code += Timer.INIT_START_TIME_VAR_CODE.format(label)
        return prefix_loop_code

    @staticmethod
    def get_suffix_loop_code(label, file_name):
        suffix_loop_code = '\n'
        suffix_loop_code += Timer.INIT_RUN_TIME_VAR_CODE.format(label)
        suffix_loop_code += Timer.WRITE_TO_FILE_CODE.format(label, file_name, label, label, label, label)
        return suffix_loop_code

    def __init__(self, file_path):
        e.assert_file_exist(file_path)
        self.__input_file_path = file_path
        self.__time_result_file = str(os.path.basename(file_path).split('.')[0]) + '_run_time_result.txt'
        self.__time_result_file = self.__time_result_file.replace(';', '')  # the file name cannot contains semicolon
        self.__number_of_loops = 0
        self.__fragmentation = Fragmentator(file_path)

    def get_input_file_path(self):
        return self.__input_file_path

    def get_time_result_file(self):
        return self.__time_result_file

    def get_fragmentation(self):
        return self.__fragmentation

    def get_number_of_loops(self):
        return self.__number_of_loops

    def set_input_file_path(self, file_path):
        e.assert_file_exist(file_path)
        self.__input_file_path = file_path

    def set_time_result_file(self, time_result_file):
        e.assert_file_from_format(time_result_file, 'txt')
        self.__time_result_file = time_result_file

    def set_fragmentation(self):
        self.__fragmentation = Fragmentator(self.__input_file_path)

    def set_number_of_loops(self, num_of_loops):
        self.__number_of_loops = num_of_loops

    def inject_timers(self):
        fragments = self.__fragmentation.fragment_code()
        with open(self.__input_file_path, 'r') as input_file:
            input_file_text = input_file.read()
        e.assert_file_is_empty(input_file_text)
        self.set_number_of_loops(len(fragments))
        if '#include <omp.h>' not in input_file_text:
            input_file_text = '#include <omp.h>\n{}'.format(input_file_text)
        if '#include <stdio.h>' not in input_file_text:
            input_file_text = '#include <stdio.h>\n{}'.format(input_file_text)
        for label, loop_fragment in enumerate(fragments, 1):
            prefix_code = self.get_prefix_loop_code(str(label))
            suffix_code = self.get_suffix_loop_code(str(label), self.__time_result_file)
            loop_with_c_code = loop_fragment['start_label'] + prefix_code
            loop_with_c_code += loop_fragment['loop']
            loop_with_c_code += suffix_code
            loop_with_c_code += loop_fragment['end_label'] + '\n'

            if 'return' in loop_with_c_code:
                loop_with_c_code = loop_with_c_code.replace('return', suffix_code + '\nreturn')

            loop_to_replace = loop_fragment['start_label'] + '\n'
            loop_to_replace += loop_fragment['loop']
            loop_to_replace += '\n' + loop_fragment['end_label']
            input_file_text = input_file_text.replace(loop_to_replace, loop_with_c_code)
        try:
            with open(self.__input_file_path, 'w') as output_file:
                output_file.write(input_file_text)
        except OSError as err:
            raise e.FileError(str(err))
