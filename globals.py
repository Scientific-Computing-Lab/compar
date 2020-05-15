import os
import enum


class GlobalsConfig:
    ASSETS_DIR_PATH = 'assets'
    LOG_EXTENSION = '.log'
    OMP_HEADER = '#include <omp.h>'
    IFDEF_OMP_HEADER = f'#ifdef _OPENMP\n{OMP_HEADER}\n#endif'
    C_STDIO_HEADER = '#include <stdio.h>'


class AutoParConfig:
    LOG_FILE_SUFFIX = '_autopar_output.log'
    OUTPUT_FILE_NAME_PREFIX = 'rose_'


class CetusConfig:
    LOG_FILE_SUFFIX = '_cetus_output.log'
    OUTPUT_DIR_NAME = 'cetus_output'


class MakefileConfig:
    EXE_FILE_EXTENSION = '.x'


class Par4allConfig:
    PIPS_STUBS_NAME = 'pips_stubs.c'
    LOG_FILE_NAME = 'par4all_output.log'
    PARALLEL_FILE_EXTENSION = '.p4a.c'


class ParallelCompilerConfig:
    PRE_PROCESSING_FILE_NAME = 'pre_processing.json'
    POST_PROCESSING_FILE_NAME = 'post_processing.json'


class CombinatorConfig:
    COMPILATION_PARAMS_FILE_NAME = 'compilation_params.json'
    OMP_RTL_PARAMS_FILE_NAME = 'omp_rtl_params.json'
    OMP_DIRECTIVES_FILE_NAME = 'omp_directives_params.json'
    COMPILATION_PARAMS_FILE_PATH = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, COMPILATION_PARAMS_FILE_NAME)
    OMP_RTL_PARAMS_FILE_PATH = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, OMP_RTL_PARAMS_FILE_NAME)
    OMP_DIRECTIVES_FILE_PATH = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, OMP_DIRECTIVES_FILE_NAME)
    PARAMS_SEPARATOR = '____compar____params____separator____'
    PARALLEL_DIRECTIVE_PREFIX = 'parallel'
    FOR_DIRECTIVE_PREFIX = 'for'


class ComparMode(enum.IntEnum):
    NEW = 0
    CONTINUE = 1
    OVERRIDE = 2


class ComparConfig:
    BACKUP_FOLDER_NAME = "backup"
    ORIGINAL_FILES_FOLDER_NAME = "original_files"
    COMBINATIONS_FOLDER_NAME = "combinations"
    SUMMARY_FILE_NAME = 'summary.csv'
    NUM_OF_THREADS = 4
    MODES = dict((mode.name.lower(), mode) for mode in ComparMode)
    DEFAULT_MODE = ComparMode.NEW.name.lower()
    COMBINATION_ID_C_COMMENT = '// COMBINATION_ID: '
    COMPILER_NAME_C_COMMENT = '// COMPILER_NAME: '
    DEFAULT_SLURM_PARTITION = 'grid'
    DEFAULT_SLURM_PARAMETERS = ['--exclusive', ]
    OPTIMAL_CURRENT_COMBINATION_FOLDER_NAME = 'current_combination'
    MIXED_COMPILER_NAME = 'mixed'


class DatabaseConfig:
    STATIC_DB_NAME = "compar_combinations"
    DYNAMIC_DB_NAME = "compar_results"
    SERVER_ADDRESS = "mongodb://10.10.10.120:27017"
    SERIAL_COMBINATION_ID = 'serial'
    COMPAR_COMBINATION_ID = 'compar_combination'
    FINAL_RESULTS_COMBINATION_ID = 'final_results'
    NAMESPACE_LENGTH_LIMIT = 120


class ExceptionConfig:
    PARAMETERS_SCHEMA_FILE_NAME = 'parameters_json_schema.json'


class ExecuteJobConfig:
    CHECK_SQUEUE_SECOND_TIME = 10
    TRY_SLURM_RECOVERY_AGAIN_SECOND_TIME = 300
    SERIAL_SPEEDUP = 1.0


class FileFormatorConfig:
    COMMENT_PREFIX = '//____compar____'
    STYLE_ARGUMENTS = [
        'AccessModifierOffset: -4',
        'IndentWidth: 4',
        'AllowShortIfStatementsOnASingleLine: false',
        'AllowShortBlocksOnASingleLine: false',
        'AllowShortFunctionsOnASingleLine: false',
        'AllowShortLoopsOnASingleLine: false',
        'SortIncludes: false'
    ]
    COLUMN_LIMIT_STYLE_ARGUMENT = 'ColumnLimit: 0'


class FragmentatorConfig:
    LOOP_LABEL_MARKER = 'LOOP_MARKER'
    START_MARKER = f'START_{LOOP_LABEL_MARKER}'
    END_MARKER = f'END_{LOOP_LABEL_MARKER}'
    START_LOOP_LABEL_MARKER = f'// {START_MARKER}'
    END_LOOP_LABEL_MARKER = f'// {END_MARKER}'


class TimerConfig:
    COMPAR_VAR_PREFIX = '____compar____'
    # WARNING! '__PREFIX_OUTPUT_FILE' var cannot contains semicolon! (be careful with hash function)
    PREFIX_OUTPUT_FILE = '#)$-@,(&=!+%^____,(&=__compar__@__should_+__be_+%___unique_(&!+$-=!+@%=!'
    COMPAR_DUMMY_VAR = f'int {COMPAR_VAR_PREFIX}dummy_var'
    TOTAL_RUNTIME_FILENAME = 'total_runtime.txt'
    LOOPS_RUNTIME_RESULTS_SUFFIX = '_run_time_result.txt'
    LOOPS_RUNTIME_SEPARATOR = ':'


class CombinationValidatorConfig:
    UNIT_TEST_FILE_NAME = 'test_output.py'
    UNIT_TEST_DEFAULT_DIR_PATH = GlobalsConfig.ASSETS_DIR_PATH
    UNIT_TEST_NAME = 'test_output'


class JobConfig:
    RUNTIME_ERROR = -1.0


class LogPhrases:
    NEW_COMBINATION = 'Working on {} combination'
    JOB_SENT_TO_SLURM = 'Job {} sent to slurm system'
    JOB_IS_COMPLETE = 'Job {} status is COMPLETE'
    TOTAL_COMBINATIONS = '{} combinations in total'
    FINAL_RESUTLS_SPEEDUP = 'final results speedup is {}'
