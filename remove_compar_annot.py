import re
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Remove Compar Annotations')
    parser.add_argument('-f', '--file', help='path to code file', required=True)
    parser.add_argument('-b', '--create_bkp', help='create a backup of the file with compar annotations',
                        action='store_true', default=False)
    # parser.add_argument('-a', '--additional_patterns', nargs="*", help='additional regex patterns to remove from file', default=[])
    args = parser.parse_args()
    args.additional_patterns = ["omp_set_num_threads\(16\);", "omp_set_dynamic\(0\);"]
    file_path = args.file
    with open(file_path) as f:
        code = f.read()

    start_loop_re = '// START_LOOP_MARKER\d+'
    code, n_subs = re.subn(start_loop_re, '', code)

    end_loop_re = '// END_LOOP_MARKERd+'
    code, n_subs = re.subn(end_loop_re, '', code)

    compar_struct_re = "\n.*____compar____[^{^;]*{[^}]*};?"
    code, n_subs = re.subn(compar_struct_re, '', code)

    compar_re = "\n.*____compar____[^;]*;"
    code, n_subs = re.subn(compar_re, '', code)

    for p in args.additional_patterns:
        code, n_subs = re.subn(p, '', code)

    if args.create_bkp:
        name, ext = os.path.splitext(file_path)
        bkp_file_path = f'{name}.compar_bkp{ext}'
        os.rename(file_path, bkp_file_path)

    with open(file_path, 'w') as f:
        f.write(code)


if __name__ == "__main__":
    main()



