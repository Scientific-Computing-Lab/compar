import os
from fragmentator import Fragmentator
import exceptions as e
import re
from globals import TimerConfig, GlobalsConfig


class Timer:

    COMPAR_VAR_PREFIX = TimerConfig.COMPAR_VAR_PREFIX
    DECL_START_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'start_time_{};\n'
    DECL_RUN_TIME_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'run_time_{};\n'
    DECL_FILE_POINTER_VAR_CODE = 'FILE *' + COMPAR_VAR_PREFIX + 'fp{};\n'
    DECL_GLOBAL_STRUCT_CODE = 'typedef struct ' + COMPAR_VAR_PREFIX + 'struct {' \
                              '\n\tint counter;\n\tdouble total_runtime;\n} ' + COMPAR_VAR_PREFIX + 'struct;\n'
    GLOBAL_TIMER_VAR_NAME = COMPAR_VAR_PREFIX + 'timer'
    INIT_GLOBAL_TIMER_VAR_CODE = GLOBAL_TIMER_VAR_NAME + ' = omp_get_wtime();\n'
    STOP_GLOBAL_TIMER_VAR_CODE = GLOBAL_TIMER_VAR_NAME + f' = omp_get_wtime() - {GLOBAL_TIMER_VAR_NAME};\n'
    DECL_GLOBAL_TIMER_VAR_CODE = 'double ' + COMPAR_VAR_PREFIX + 'timer;'
    INIT_START_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'start_time_{} = omp_get_wtime();\n'
    INIT_RUN_TIME_VAR_CODE = COMPAR_VAR_PREFIX + 'run_time_{} = omp_get_wtime() - ' +\
        COMPAR_VAR_PREFIX + 'start_time_{};\n'

    WRITE_TO_FILE_CODE_1 = 'FILE * fp{} = fopen(\"{}\", \"w\");\n'
    WRITE_TO_FILE_CODE_2 = 'fprintf(fp{}, '+'"'+'%d' + TimerConfig.LOOPS_RUNTIME_SEPARATOR + \
                           '%.10lf'+r'\\n' + '"' + ', {}, {});\n'  # <loop number>:<run time>
    WRITE_TO_FILE_CODE_3 = 'fclose(fp{});\n'
    WRITE_TO_FILE_CODE_4 = 'fprintf(fp{}, ' + '"' + '%.10lf' + r'\\n' + '"' + ', {});\n'
    COMPAR_DUMMY_VAR = TimerConfig.COMPAR_DUMMY_VAR
    TOTAL_RUNTIME_FILENAME = TimerConfig.TOTAL_RUNTIME_FILENAME
    NAME_OF_GLOBAL_ARRAY = f'{COMPAR_VAR_PREFIX}arr'
    DECL_GLOBAL_ARRAY = COMPAR_VAR_PREFIX + "struct {}[{}] = {{0}};\n"

    @staticmethod
    def get_file_name_prefix_token():
        return TimerConfig.PREFIX_OUTPUT_FILE

    @staticmethod
    def get_declarations_code(label):
        declaration_code = '\n'
        declaration_code += Timer.DECL_START_TIME_VAR_CODE.format(label)
        declaration_code += Timer.DECL_RUN_TIME_VAR_CODE.format(label)
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

    @staticmethod
    def remove_declaration_code(content):
        run_time_vars_regex = rf'double[ ]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        file_pointer_vars_regex = rf'FILE[ ]*\*[ ]*{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        struct_regex_version_1 = r'typedef struct ' + Timer.COMPAR_VAR_PREFIX + r'[^\}]*\}[^;]*;'
        struct_regex_version_2 = r'struct ' + Timer.COMPAR_VAR_PREFIX + r'[^\}]+int[^\}]+\}[^;]*;'
        struct_regex_version_3 = r'typedef struct ' + Timer.COMPAR_VAR_PREFIX
        struct_regex_version_3 + r'[^\;]*' + Timer.COMPAR_VAR_PREFIX + r';'
        compar_dummy_var_regex = fr'{Timer.COMPAR_DUMMY_VAR}[^;]+;'
        content = re.sub(rf'{Timer.DECL_GLOBAL_TIMER_VAR_CODE}', '', content)
        content = re.sub(struct_regex_version_1, '', content, flags=re.DOTALL)
        content = re.sub(struct_regex_version_2, '', content, flags=re.DOTALL)
        content = re.sub(struct_regex_version_3, '', content, flags=re.DOTALL)
        content = re.sub(run_time_vars_regex, '', content, flags=re.DOTALL)
        content = re.sub(file_pointer_vars_regex, '', content, flags=re.DOTALL)
        content = re.sub(compar_dummy_var_regex, '', content, flags=re.DOTALL)
        return content

    @staticmethod
    def remove_run_time_calculation_code_code(content):
        content = re.sub(rf'{Timer.GLOBAL_TIMER_VAR_NAME}[^;]+omp_get_wtime[^;]+;', '', content)
        content = re.sub(rf'{Timer.COMPAR_VAR_PREFIX}[^;]+=[ ]*\(?[ ]*omp[^;]*;', '', content, flags=re.DOTALL)
        content = re.sub(rf'{Timer.COMPAR_VAR_PREFIX}struct[ ]+extern[^;]+;', '', content, flags=re.DOTALL)
        content = re.sub(Timer.COMPAR_VAR_PREFIX + r'struct[^\}]+arr[^\}]+\}[ ]*;', '', content, flags=re.DOTALL)
        return re.sub(rf'{Timer.COMPAR_VAR_PREFIX}arr[^;]+;', '', content, flags=re.DOTALL)

    @staticmethod
    def remove_writing_to_file_code(content):
        fopen_regex = rf'{Timer.COMPAR_VAR_PREFIX}[^;]+fopen[^;]+{re.escape(Timer.get_file_name_prefix_token())}?[^;]+;'
        fprintf_regex = rf'fprintf[^;]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        fclose_regex = rf'fclose[^;]+{Timer.COMPAR_VAR_PREFIX}[^;]+;'
        main_file_at_exit_regex = r'void[ ]+' + Timer.COMPAR_VAR_PREFIX + r'atExit[^\}]+\}'
        main_file_at_exit_call_regex = r'atexit[^\;]+;'
        content = re.sub(main_file_at_exit_regex, '', content, flags=re.DOTALL)
        content = re.sub(main_file_at_exit_call_regex, '', content, flags=re.DOTALL)
        content = re.sub(fopen_regex, '', content, flags=re.DOTALL)
        content = re.sub(fprintf_regex, '', content, flags=re.DOTALL)
        content = re.sub(fclose_regex, '', content, flags=re.DOTALL)
        return content

    @staticmethod
    def remove_timer_code(absolute_file_paths_list):
        for c_file_dict in absolute_file_paths_list:
            try:
                with open(c_file_dict['file_full_path'], 'r') as f:
                    content = f.read()
                content = Timer.remove_declaration_code(content)
                content = Timer.remove_run_time_calculation_code_code(content)
                content = Timer.remove_writing_to_file_code(content)
                with open(c_file_dict['file_full_path'], 'w') as f:
                    f.write(content)
            except Exception as ex:
                raise e.FileError(f'exception in Compar.remove_timer_code: {c_file_dict["file_full_path"]}: {str(ex)}')

    def __init__(self, file_path, code_with_markers=False):
        e.assert_file_exist(file_path)
        self.__input_file_path = file_path
        c_file_name = str(os.path.basename(file_path).split('.')[0])
        self.__time_result_file = c_file_name + TimerConfig.LOOPS_RUNTIME_RESULTS_SUFFIX
        self.__time_result_file = self.__time_result_file.replace(';', '')  # the file name cannot contains semicolon
        self.__number_of_loops = 0
        self.__fragmentation = Fragmentator(file_path, code_with_markers)

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
        name_of_global_array = f'{self.COMPAR_VAR_PREFIX}arr{str(array_var_index)}'
        input_file_text, fragments = self.calculate_num_of_loops()

        if self.__input_file_path != main_file_path and self.get_number_of_loops() != 0:
            input_file_text = Timer.inject_global_declaration(
                input_file_text, self.__number_of_loops, name_of_global_array)

        if GlobalsConfig.OMP_HEADER not in input_file_text:
            input_file_text = f'{GlobalsConfig.IFDEF_OMP_HEADER}\n{input_file_text}'
        if GlobalsConfig.C_STDIO_HEADER not in input_file_text:
            input_file_text = f'{GlobalsConfig.C_STDIO_HEADER}\n{input_file_text}'
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
            code = 'void ' + Timer.COMPAR_VAR_PREFIX + 'atExit() {\n'
            total_runtime_file_path = os.path.join(working_dir_path, Timer.TOTAL_RUNTIME_FILENAME)
            code += f'{Timer.STOP_GLOBAL_TIMER_VAR_CODE}'
            code += Timer.WRITE_TO_FILE_CODE_1.format(Timer.GLOBAL_TIMER_VAR_NAME, total_runtime_file_path)
            code += Timer.WRITE_TO_FILE_CODE_4.format(Timer.GLOBAL_TIMER_VAR_NAME, Timer.GLOBAL_TIMER_VAR_NAME)
            code += Timer.WRITE_TO_FILE_CODE_3.format(Timer.GLOBAL_TIMER_VAR_NAME)
            code += '}\n'
            code_to_replace += code
            new_code = f'{code_to_replace} atexit({Timer.COMPAR_VAR_PREFIX}atExit);\n'
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
            new_code += f'{code_to_replace} atexit({Timer.COMPAR_VAR_PREFIX}atExit);\n'
            new_code += f'{Timer.INIT_GLOBAL_TIMER_VAR_CODE}'

            c_code = re.sub(regex_pattern, new_code, input_file_text)
            with open(main_file_path, 'w') as output_file:
                output_file.write(c_code)

    @staticmethod
    def inject_global_declaration(input_file_text, num_of_loops, name_of_global_array):
        new_code = Timer.DECL_GLOBAL_STRUCT_CODE
        new_code += f"{Timer.COMPAR_VAR_PREFIX}struct extern {name_of_global_array}[{num_of_loops}];\n"
        new_code += input_file_text
        return new_code

    @staticmethod
    def generate_at_exit_function_code(files_loop_dict, working_dir_path):
        code = 'void ' + Timer.COMPAR_VAR_PREFIX + 'atExit() {\n'
        total_runtime_file_path = os.path.join(working_dir_path, Timer.TOTAL_RUNTIME_FILENAME)
        code += f'{Timer.STOP_GLOBAL_TIMER_VAR_CODE}'
        code += Timer.WRITE_TO_FILE_CODE_1.format(Timer.GLOBAL_TIMER_VAR_NAME, total_runtime_file_path)
        code += Timer.WRITE_TO_FILE_CODE_4.format(Timer.GLOBAL_TIMER_VAR_NAME, Timer.GLOBAL_TIMER_VAR_NAME)
        code += Timer.WRITE_TO_FILE_CODE_3.format(Timer.GLOBAL_TIMER_VAR_NAME)
        for file, loops in files_loop_dict.items():
            if loops[0] != 0:  # the file has loops
                name, ext = os.path.splitext(file)
                new_file_name = f'{name}{TimerConfig.LOOPS_RUNTIME_RESULTS_SUFFIX}'
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
