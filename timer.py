import os
from fragmentator import Fragmentator
import exceptions as e
import re


class Timer(object):

    COMPAR_VAR_PREFIX = '____compar____'
    # WARNING! '__PREFIX_OUTPUT_FILE' var cannot contains semicolon!
    __PREFIX_OUTPUT_FILE = '#)$-@,(&=!+%^____,(&=__compar__@__should_+__be_+%___unique_(&!+$-=!+@%=!'
    DECL_START_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'start_time_{};\n'
    DECL_RUN_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'run_time_{};\n'
    DECL_FILE_POINTER_VAR_CODE = 'FILE *' + COMPAR_VAR_PREFIX + 'fp{};\n'
    DECL_GLOBAL_STRUCT_CODE = 'typedef struct ____compar____struct {' \
                              '\n\tint counter;\n\tdouble total_runtime;\n} ____compar____struct;\n'
    GLOBAL_TIMER_VAR_NAME = COMPAR_VAR_PREFIX + 'timer'
    INIT_GLOBAL_TIMER_VAR_CODE = GLOBAL_TIMER_VAR_NAME + ' = omp_get_wtime();\n'
    STOP_GLOBAL_TIMER_VAR_CODE = GLOBAL_TIMER_VAR_NAME + f' = omp_get_wtime() - {GLOBAL_TIMER_VAR_NAME};\n'
    DECL_GLOBAL_TIMER_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'timer;'
    INIT_START_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'start_time_{} = omp_get_wtime();\n'
    INIT_RUN_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'run_time_{} = omp_get_wtime() - ' +\
                             COMPAR_VAR_PREFIX + 'start_time_{};\n'

    WRITE_TO_FILE_CODE_1 = 'FILE * fp{} = fopen(\"{}\", \"w\");\n'
    WRITE_TO_FILE_CODE_2 = 'fprintf(fp{}, '+'"'+'run time of loop %d: %.10lf'+r'\\n' + '"' + ', {}, {});\n'
    WRITE_TO_FILE_CODE_3 = 'fclose(fp{});\n'
    WRITE_TO_FILE_CODE_4 = 'fprintf(fp{}, ' + '"' + '%.10lf' + r'\\n' + '"' + ', {});\n'
    COMPAR_DUMMY_VAR = f'int {COMPAR_VAR_PREFIX}dummy_var'
    TOTAL_RUNTIME_FILENAME = 'total_runtime.txt'

    @staticmethod
    def get_file_name_prefix_token():
        return Timer.__PREFIX_OUTPUT_FILE

    @staticmethod
    def get_declarations_code(label):
        declaration_code = '\n'
        declaration_code += Timer.DECL_START_TIME_VAR_CODE.format(label)
        declaration_code += Timer.DECL_RUN_TIME_VAR_CODE.format(label)
        #TODO: declaration_code += Timer.DECL_FILE_POINTER_VAR_CODE.format(label)
        return declaration_code

    @staticmethod
    def get_prefix_loop_code(label):
        prefix_loop_code = '\n'
        prefix_loop_code += Timer.get_declarations_code(label)
        prefix_loop_code += Timer.INIT_START_TIME_VAR_CODE.format(label)
        return prefix_loop_code

    @staticmethod
    def get_suffix_loop_code(label, name_of_global_array):
        suffix_loop_code = '\n'
        suffix_loop_code += Timer.INIT_RUN_TIME_VAR_CODE.format(label, label)
        suffix_loop_code += f'{name_of_global_array}[{int(label)-1}].counter++;\n'
        suffix_loop_code += f'{name_of_global_array}[{int(label)-1}].total_runtime+=' \
            f'{Timer.COMPAR_VAR_PREFIX}run_time_{label};\n'
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

    def calculate_num_of_loops(self):
        fragments = self.__fragmentation.fragment_code()
        with open(self.__input_file_path, 'r') as input_file:
            input_file_text = input_file.read()
        e.assert_file_is_empty(input_file_text)
        self.set_number_of_loops(len(fragments))
        return input_file_text, fragments

    def inject_timers(self, array_var_index, main_file_path):
        name_of_global_array = f'____compar____arr{str(array_var_index)}'
        input_file_text, fragments = self.calculate_num_of_loops()

        if self.__input_file_path != main_file_path and self.get_number_of_loops() != 0:
            input_file_text = Timer.inject_global_declaration(
                input_file_text, self.__number_of_loops, name_of_global_array)

        if '#include <omp.h>' not in input_file_text:
            input_file_text = f'#ifdef _OPENMP\n#include <omp.h>\n#endif\n{input_file_text}'
        if '#include <stdio.h>' not in input_file_text:
            input_file_text = f'#include <stdio.h>\n{input_file_text}'
        for label, loop_fragment in enumerate(fragments, 1):
            prefix_code = self.get_prefix_loop_code(str(label))
            suffix_code = self.get_suffix_loop_code(str(label), name_of_global_array)
            loop_with_c_code = loop_fragment['start_label'] + prefix_code
            loop_with_c_code += loop_fragment['loop']
            loop_with_c_code += suffix_code
            loop_with_c_code += loop_fragment['end_label'] + '\n' + Timer.COMPAR_DUMMY_VAR + str(label) + ';\n'

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

    @staticmethod
    def inject_timer_to_compar_mixed_file(file_path, working_dir_path):
        with open(file_path, 'r') as input_file:
            input_file_text = Timer.DECL_GLOBAL_TIMER_VAR_CODE + "\n"
            input_file_text += input_file.read()
            with open(file_path, 'w') as output_file:
                output_file.write(input_file_text)

        with open(file_path, 'r') as input_file:
            input_file_text = input_file.read()
            regex_pattern = "((int|void)[ ]*main[ ]*[(].*[)][ ]*[\\n]?{\\n)"
            code_to_replace = re.findall(regex_pattern, input_file_text)
            if len(code_to_replace) < 1:
                raise Exception('atexit function could not be injected.')
            code_to_replace = code_to_replace[0][0]
            code = 'void ____compar____atExit() {\n'
            total_runtime_file_path = os.path.join(working_dir_path, Timer.TOTAL_RUNTIME_FILENAME)
            code += f'{Timer.STOP_GLOBAL_TIMER_VAR_CODE}'
            code += Timer.WRITE_TO_FILE_CODE_1.format(Timer.GLOBAL_TIMER_VAR_NAME, total_runtime_file_path)
            code += Timer.WRITE_TO_FILE_CODE_4.format(Timer.GLOBAL_TIMER_VAR_NAME, Timer.GLOBAL_TIMER_VAR_NAME)
            code += Timer.WRITE_TO_FILE_CODE_3.format(Timer.GLOBAL_TIMER_VAR_NAME)
            code += '}\n'
            code_to_replace += code
            new_code = f'{code_to_replace} atexit(____compar____atExit);\n'
            new_code += f'{Timer.INIT_GLOBAL_TIMER_VAR_CODE}'
            c_code = re.sub(regex_pattern, new_code, input_file_text)
            with open(file_path, 'w') as output_file:
                output_file.write(c_code)

    @staticmethod
    def inject_declarations_to_main_file(file_path, declaration_code_to_inject):
        with open(file_path, 'r') as input_file:
            input_file_text = Timer.DECL_GLOBAL_STRUCT_CODE
            input_file_text += Timer.DECL_GLOBAL_TIMER_VAR_CODE + "\n"
            input_file_text += declaration_code_to_inject + "\n"
            input_file_text += input_file.read()
            with open(file_path, 'w') as output_file:
                output_file.write(input_file_text)

    @staticmethod
    def inject_atexit_code_to_main_file(main_file_path, files_loop_dict, working_dir_path):
        with open(main_file_path, 'r') as input_file:
            input_file_text = input_file.read()

            regex_pattern = "((int|void)[ ]*main[ ]*[(].*[)][ ]*[\\n]?{\\n)"
            code_to_replace = re.findall(regex_pattern, input_file_text)
            if len(code_to_replace) < 1:
                raise Exception('atexit function could not be injected.')

            code_to_replace = code_to_replace[0][0]

            new_code = Timer.generate_at_exit_function_code(files_loop_dict, working_dir_path)
            new_code += f'{code_to_replace} atexit(____compar____atExit);\n'
            new_code += f'{Timer.INIT_GLOBAL_TIMER_VAR_CODE}'

            c_code = re.sub(regex_pattern, new_code, input_file_text)
            with open(main_file_path, 'w') as output_file:
                output_file.write(c_code)

    @staticmethod
    def inject_global_declaration(input_file_text, num_of_loops, name_of_global_array):
        new_code = Timer.DECL_GLOBAL_STRUCT_CODE
        new_code += f"____compar____struct extern {name_of_global_array}[{num_of_loops}];\n"
        new_code += input_file_text
        return new_code

    @staticmethod
    def generate_at_exit_function_code(files_loop_dict, working_dir_path):
        code = 'void ____compar____atExit() {\n'
        total_runtime_file_path = os.path.join(working_dir_path, Timer.TOTAL_RUNTIME_FILENAME)
        code += f'{Timer.STOP_GLOBAL_TIMER_VAR_CODE}'
        code += Timer.WRITE_TO_FILE_CODE_1.format(Timer.GLOBAL_TIMER_VAR_NAME, total_runtime_file_path)
        code += Timer.WRITE_TO_FILE_CODE_4.format(Timer.GLOBAL_TIMER_VAR_NAME, Timer.GLOBAL_TIMER_VAR_NAME)
        code += Timer.WRITE_TO_FILE_CODE_3.format(Timer.GLOBAL_TIMER_VAR_NAME)
        for file, loops in files_loop_dict.items():
            if loops[0] != 0:  # the file has loops
                name, ext = os.path.splitext(file)
                new_file_name = f'{name}_run_time_result.txt'
                path = os.path.join(working_dir_path, new_file_name)
                code += Timer.WRITE_TO_FILE_CODE_1.format(loops[1], path)
                curr_loop = 0
                while curr_loop < loops[0]:
                    code += f'if ({loops[1]}[{curr_loop}].counter > 0) '
                    code += Timer.WRITE_TO_FILE_CODE_2.format(loops[1], curr_loop+1,
                                                              f'{loops[1]}[{curr_loop}].total_runtime')
                    curr_loop += 1
                code += Timer.WRITE_TO_FILE_CODE_3.format(loops[1])
        code += '}\n'
        return code
