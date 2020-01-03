import os
from fragmentator import Fragmentator
import exceptions as e


class Timer(object):

    @staticmethod
    def get_c_code_calculate_time(time_label):
        c_code_calculate_time = 'double ' + time_label + ';\n' \
                 + time_label + ' = omp_get_wtime();\n'
        return c_code_calculate_time

    def __init__(self, file_path):
        e.assert_file_exist(file_path)
        self.__input_file_path = file_path
        self.__time_result_file = os.path.basename(file_path).split('.')[0] + '_run_time_result.txt'
        self.__c_code_calculate_initial_time = ''
        self.__c_code_calculate_run_time = ''
        self.__c_code_write_to_file = ''
        self.__fragmentation = Fragmentator(file_path)

    def get_input_file_path(self):
        return self.__input_file_path

    def get_time_result_file(self):
        return self.__time_result_file

    def get_c_code_calculate_initial_time(self):
        return self.__c_code_calculate_initial_time

    def get_c_code_calculate_run_time(self):
        return self.__c_code_calculate_run_time

    def get_c_code_write_to_file(self):
        return self.__c_code_write_to_file

    def get_fragmentation(self):
        return self.__fragmentation

    def set_input_file_path(self, file_path):
        e.assert_file_exist(file_path)
        self.__input_file_path = file_path

    def set_time_result_file(self, time_result_file):
        e.assert_file_from_format(time_result_file, 'txt')
        self.__time_result_file = time_result_file

    def set_c_code_calculate_initial_time(self, start_time_label):
        self.__c_code_calculate_initial_time = Timer.get_c_code_calculate_time(start_time_label)

    def set_c_code_calculate_run_time(self, run_time_label):
        self.__c_code_calculate_run_time = '\n' + Timer.get_c_code_calculate_time(run_time_label)

    def set_c_code_write_to_file(self, fp_label, label, run_time_var):
        c_code = 'FILE *' + fp_label + ';\n' \
                 + fp_label + ' = fopen(' + self.__time_result_file + ', "a");\n' \
                 'fprintf(' + fp_label + ', "\\nrun time of loop %d: %lf", ' \
                 + label + ', ' + run_time_var + ');\nfclose(' + fp_label + ');\n'
        self.__c_code_write_to_file = c_code

    def set_fragmentation(self):
        self.__fragmentation = Fragmentator(self.__input_file_path)

    def inject_timers(self):
        with open(self.__input_file_path, 'r') as input_file:
            input_file_text = input_file.read()
        e.assert_file_is_empty(input_file_text)
        input_file_text = '#include <omp.h>\n{}'.format(input_file_text)
        fragments = self.__fragmentation.fragment_code()
        for loop_fragment, label in zip(fragments, range(1, len(fragments)+1)):
            loop_with_c_code = ''
            c_code_start_time_var = 'start_time_' + str(label)
            c_code_run_time_var = 'run_time_' + str(label)
            c_code_fp_var = 'fp_' + str(label)
            self.set_c_code_calculate_initial_time(c_code_start_time_var)
            self.set_c_code_calculate_run_time(c_code_run_time_var)
            self.set_c_code_write_to_file(c_code_fp_var, str(label), c_code_run_time_var)
            loop_with_c_code += self.__c_code_calculate_initial_time + loop_fragment['loop'] + \
                                self.__c_code_calculate_run_time + self.__c_code_write_to_file
            input_file_text = input_file_text.replace(loop_fragment['loop'], loop_with_c_code)
        try:
            with open(self.__input_file_path, 'w') as output_file:
                output_file.write(input_file_text)
        except OSError as err:
            raise e.FileError(str(err))


t = Timer('test.txt')
t.inject_timers()
print(t)

