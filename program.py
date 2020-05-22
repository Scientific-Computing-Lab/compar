import argparse
from compar import Compar
import traceback
import logger
from globals import ComparConfig


def positive_int_validation(value):
    exception = argparse.ArgumentTypeError(f'{value} must be a positive integer value')
    try:
        int_value = int(value)
    except ValueError:
        raise exception
    if int_value <= 0:
        raise exception
    return int_value


def main():
    num_of_jobs_at_once = 4
    parser = argparse.ArgumentParser(description='ComPar')
    parser.add_argument('-input_dir', '--input_directory_path', help='Input directory path', required=True)
    parser.add_argument('-output_dir', '--output_directory_path', help='Output directory path', required=True)
    parser.add_argument('-name', '--project_name', help='Project name', required=True)
    parser.add_argument('-comp', '--binary_compiler_type', help='Binary compiler type', default="")
    parser.add_argument('-comp_v', '--binary_compiler_version', help='Binary compiler version', default=None)
    parser.add_argument('-comp_f', '--binary_compiler_flags', nargs="*", help='Binary compiler flags', default=None)
    parser.add_argument('-save_folders', '--save_combinations_folders', help='Save all combinations folders',
                        action='store_true', default=False)
    parser.add_argument('-make', '--is_make_file', help='Use makefile flag', action='store_true')
    parser.add_argument('-make_c', '--makefile_commands', nargs="*", help='Makefile commands', default=None)
    parser.add_argument('-make_op', '--makefile_exe_folder_rel_path',
                        help='Makefile output executable folder relative path to input directory',
                        default="")
    parser.add_argument('-make_on', '--makefile_output_exe_file_name', help='Makefile output executable file name',
                        default="")
    parser.add_argument('-ignore', '--ignored_rel_paths', nargs="*",
                        help='List of relative folder paths to be ignored while parallelizing', default=None)
    parser.add_argument('-include', '--include_dirs_list', nargs="*",
                        help='Include dir names for compilation - relative paths', default=None)
    parser.add_argument('-main_file_p', '--main_file_parameters', nargs="*", help='Main c file parameters',
                        default=None)
    parser.add_argument('-slurm_p', '--slurm_parameters', nargs="*", help='Slurm parameters', default=['--exclusive', ])
    parser.add_argument('-extra', '--extra_files', nargs="*", default=None,
                        help='List of relative extra files to parallelize in addition to current ones.')
    parser.add_argument('-main_file_r_p', '--main_file_rel_path', help='Main c file name relative path',
                        default="", required=True)
    parser.add_argument('-t', '--time_limit', help='Time limit for runtime execution', default=None)
    parser.add_argument('-partition', '--slurm_partition', help='Slurm partition name', default='grid')
    parser.add_argument('-v', '--verbose', help="Get more verbose output", action="store_const", dest="log_level",
                        const=logger.VERBOSE, default=logger.BASIC)
    parser.add_argument('-vv', '--debug', help="Get debug output", action="store_const", dest="log_level",
                        const=logger.DEBUG, default=logger.BASIC)
    parser.add_argument('-test_file', '--test_file_path', help="Unit test file path", default="")
    parser.add_argument('-jobs_quantity', '--jobs_quantity_at_once', help='The number of jobs to be executed at once',
                        default=num_of_jobs_at_once, type=positive_int_validation)
    parser.add_argument('-mode', '--mode', help=f'Compar working mode {ComparConfig.MODES.keys()}.',
                        default=ComparConfig.DEFAULT_MODE, choices=ComparConfig.MODES.keys())
    parser.add_argument('-with_markers', '--code_with_markers', action='store_true',
                        help='Mark that the code was parallelized with Compar before')
    parser.add_argument('-clear_db', '--clear_db', action='store_true', help='Delete the results from database.')
    parser.add_argument('-multiple_combinations', '--multiple_combinations', type=positive_int_validation, default=1,
                        help='Number of times to repeat each combination.')
    args = parser.parse_args()
    args.mode = ComparConfig.MODES[args.mode]

    Compar.set_num_of_threads(args.jobs_quantity_at_once)
    compar_obj = Compar(
        input_dir=args.input_directory_path,
        output_dir=args.output_directory_path,
        project_name=args.project_name,
        binary_compiler_type=args.binary_compiler_type.lower(),
        binary_compiler_version=args.binary_compiler_version,
        binary_compiler_flags=args.binary_compiler_flags,
        save_combinations_folders=args.save_combinations_folders,
        is_make_file=args.is_make_file,
        makefile_commands=args.makefile_commands,
        makefile_exe_folder_rel_path=args.makefile_exe_folder_rel_path,
        makefile_output_exe_file_name=args.makefile_output_exe_file_name,
        ignored_rel_paths=args.ignored_rel_paths,
        include_dirs_list=args.include_dirs_list,
        main_file_parameters=args.main_file_parameters,
        slurm_parameters=args.slurm_parameters,
        extra_files=args.extra_files,
        main_file_rel_path=args.main_file_rel_path,
        time_limit=args.time_limit,
        slurm_partition=args.slurm_partition,
        test_file_path=args.test_file_path,
        mode=args.mode,
        code_with_markers=args.code_with_markers,
        clear_db=args.clear_db,
        multiple_combinations=args.multiple_combinations,
        log_level=args.log_level
    )
    try:
        compar_obj.fragment_and_add_timers()
        compar_obj.run_serial()
        compar_obj.run_parallel_combinations()
        compar_obj.generate_optimal_code()
        logger.info('Finish Compar execution')
    except Exception:
        if args.clear_db:
            compar_obj.clear_related_collections()
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.info_error(f'Exception at Compar Program: {e}')
        logger.debug_error(traceback.format_exc())
        exit(1)
