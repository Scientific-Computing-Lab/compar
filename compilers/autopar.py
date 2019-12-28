import subprocess
import os
from distutils.dir_util import copy_tree
from shutil import copy
import time


benchmarks = ["BT", "CG", "EP", "LU", "MG", "SP", "UA"]

def main():
    
    # CLEAN BIN FOLDER
    process = subprocess.Popen(['bash','-c', "rm -f bin/*"]) 
    process.wait()

    print("********** START SERIAL BENCHMARKS COMPILING **********")
    for benchmark in benchmarks:
        print("Benchmark "+benchmark+" compiling...")
        try:
            process = subprocess.Popen(['bash','-c', "make " + benchmark + " CLASS=C"])
            process.wait()
        except Exception as e:
            print(e)
            print("Benchmark " + benchmark + " failed to compile!")
        
    print("********** START SERIAL BENCHMARKS EXECUTION **********")

    process = subprocess.Popen(['bash','-c', "python3 run_tests.py -dir bin -p grid -sbatch"])
    process.wait()
    
    
    # CLEAN BIN FOLDER
    process = subprocess.Popen(['bash','-c', "rm -f parallel_benchmarks/bin/*"])
    process.wait()

    # COPY NECESSRARY FILES
    print("********** STARTING PARALLEL ENVOIRNMENT **********")
    try:
        if not os.path.exists(os.path.dirname("parallel_benchmarks/bin/")):
            os.makedirs(os.path.dirname("parallel_benchmarks/bin/"))
    except OSError as err:
        print(err)
    copy("Makefile", "parallel_benchmarks/")
    copy_tree("common", "parallel_benchmarks/common/")
    copy_tree("config", "parallel_benchmarks/config/")
    copy_tree("sys", "parallel_benchmarks/sys/")

    print("********** START PARALLEL BENCHMARKS COMPILING **********")

    for benchmark in benchmarks:
        print("Benchmark "+benchmark+" being parallel...")
        try:
            process = subprocess.Popen(['bash','-c', "python3 autoPar_script.py -dir " + benchmark])
            process.wait()
        except:
            print("Benchmark " + benchmark + " failed to be parallel!")

        print("Benchmark "+benchmark+" compiling...")
        try:
            process = subprocess.Popen(['bash','-c', "make " + benchmark + " CLASS=C -C parallel_benchmarks/"])
            process.wait()
        except:
            print("Benchmark " + benchmark + " failed to compile!")

    print("********** START PARALLEL BENCHMARKS EXECUTION **********")
    
    subprocess.Popen(['bash','-c', "python3 run_tests.py -dir parallel_benchmarks/bin -p grid -sbatch"])


if __name__ == "__main__":
    main()
