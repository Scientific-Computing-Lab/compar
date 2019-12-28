import argparse
import os
import subprocess
import distutils
import time
from distutils import dir_util

def run_test(f_name, dest_dir, options):
    print ("starting test "+ f_name)
    sub_proc = subprocess.Popen(['autoPar'] + options + [f_name, f_name], cwd=dest_dir)
    sub_proc.wait()
    print ("done parallel work")

def main(dir, options):

    dir = os.path.abspath(dir)
    dir_name = os.path.basename(dir)

    for root, dirs, files in os.walk(dir):
        for name in files:
            if os.path.splitext(name)[1] == '.c':
                run_test(name, dir, options)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs tests with varying input sizes.')
    parser.add_argument('-dir', dest='dir', help='Path to the directory containing the tests.')
    parser.add_argument('-options', dest='options', nargs='+', default="")
    args = parser.parse_args()

    main(args.dir, args.options[0].split(" "))