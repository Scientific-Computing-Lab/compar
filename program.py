import argparse
from compar import Compar
import traceback
import os
import shutil
from exceptions import assert_rel_path_starts_without_sep
import logger


def main():
    num_of_jobs_at_once = 4
    logger.info('Starting Compar execution')
    parser = argparse.ArgumentParser(description='Compar')
    parser.add_argument('-wd', '--working_directory', help='Working directory path', required=True)
    parser.add_argument('-dir', '--input_dir', help='Input directory path', required=True)
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
    parser.add_argument('-nas', '--is_nas', help='Is NAS Benchmark', action='store_true')
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
                        default=num_of_jobs_at_once)
    args = parser.parse_args()

    # TODO: should be depend on users choice
    if os.path.exists(args.working_directory):
        shutil.rmtree(args.working_directory)
    os.mkdir(args.working_directory)

    assert_rel_path_starts_without_sep(args.makefile_exe_folder_rel_path)
    for path in args.makefile_exe_folder_rel_path:
        assert_rel_path_starts_without_sep(path)

    if args.slurm_parameters and len(args.slurm_parameters) == 1:
        args.slurm_parameters = str(args.slurm_parameters[0]).split(' ')

    logger.initialize(args.log_level)

    Compar.set_num_of_threads(args.jobs_quantity_at_once)
    compar_obj = Compar(
        working_directory=args.working_directory,
        input_dir=args.input_dir,
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
        is_nas=args.is_nas,
        main_file_rel_path=args.main_file_rel_path,
        time_limit=args.time_limit,
        slurm_partition=args.slurm_partition,
        test_file_path=args.test_file_path
    )
    # TODO: change fragment_and_add_timers main file path
    compar_obj.fragment_and_add_timers()
    compar_obj.run_serial()
    compar_obj.run_parallel_combinations()
    compar_obj.generate_optimal_code()
    logger.info('Finish Compar execution')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.info_error(f'Exception at Compar Program: {e}')
        logger.debug_error(traceback.format_exc())
