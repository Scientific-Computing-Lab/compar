import argparse
from compar import Compar
import traceback
import os
import shutil


def main():
    parser = argparse.ArgumentParser(description='Compar')
    parser.add_argument('-wd', '--working_directory', help='Working directory path', required=True)
    parser.add_argument('-dir', '--input_dir', help='Input directory path', required=True)
    parser.add_argument('-comp', '--binary_compiler_type', help='Binary compiler type', required=True)
    parser.add_argument('-comp_v', '--binary_compiler_version', help='Binary compiler version', required=True)
    parser.add_argument('-comp_f', '--binary_compiler_flags', nargs="*", help='Binary compiler flags', default=None)
    parser.add_argument('-save_folders', '--delete_combinations_folders', help='Save all combinations folders',
                        action='store_false')
    parser.add_argument('-make', '--is_make_file', help='Use makefile flag', action='store_true')
    parser.add_argument('-make_c', '--makefile_commands', nargs="*", help='Makefile commands', default=None)
    parser.add_argument('-make_op', '--makefile_output_exe_folder', help='Makefile output executable folder',
                        default="")
    parser.add_argument('-make_on', '--makefile_output_exe_file_name', help='Makefile output executable file name',
                        default="")
    parser.add_argument('-p4a_f', '--par4all_flags', nargs="*", help='Par4all flags', default=None)
    parser.add_argument('-autopar_f', '--autopar_flags', nargs="*", help='Autopar flags', default=None)
    parser.add_argument('-cetus_f', '--cetus_flags', nargs="*", help='Cetus flags', default=None)
    parser.add_argument('-main_file', '--main_file_name', help='Main c file name', default="")
    parser.add_argument('-main_file_p', '--main_file_parameters', nargs="*", help='Main c file parameters', default=None)
    parser.add_argument('-slurm_p', '--slurm_parameters', nargs="*", help='Slurm parameters', default=None)
    args = vars(parser.parse_args())

    # TODO: should be depend on users choice
    if os.path.exists(args['working_directory']):
        shutil.rmtree(args['working_directory'])
    os.mkdir(args['working_directory'])

    compar_obj = Compar(
        working_directory=args['working_directory'],
        input_dir=args['input_dir'],
        binary_compiler_type=args['binary_compiler_type'],
        binary_compiler_version=['args.binary_compiler_version'],
        binary_compiler_flags=args['binary_compiler_flags'],
        delete_combinations_folders=args['delete_combinations_folders'],
        is_make_file=args['is_make_file'],
        makefile_commands=args['makefile_commands'],
        makefile_output_exe_folder=args['makefile_output_exe_folder'],
        makefile_output_exe_file_name=args['makefile_output_exe_file_name'],
        par4all_flags=args['par4all_flags'],
        autopar_flags=args['autopar_flags'],
        cetus_flags=args['cetus_flags'],
        main_file_name=args['main_file_name'],
        main_file_parameters=args['main_file_parameters'],
        slurm_parameters=args['slurm_parameters']
    )
    compar_obj.fragment_and_add_timers()
    compar_obj.run_serial()
    compar_obj.run_parallel_combinations()
    compar_obj.generate_optimal_code()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
