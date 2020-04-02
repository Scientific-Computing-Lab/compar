# ComPar

ComPar is a source-to-source compiler that generates the best parallelized code (in terms of performances) which can be achieved from automatic parallelization compilers without any human intervention. This is done by fusing other source-to-source compilers' outputs. The only human intervention in ComPar is by supporting the source code to be parallelized and setting the desired hyperparameters (i.e. the parameters defined by the different compilers and OpenMP) in a JSON format. Afterwards, ComPar divides the source code into loop segments, and from the provided JSON file it creates different combinations of these parameters. The combinations are assembled with the code segments and each segment is run by all of the compilers. Finally, ComPar chooses the best combination for the given code, i.e. the combination with the shortest execution time, while removing unnecessary parallelization pragmas.

**Note:** The correctness of the input parameters affects the correctness of the parallelized code. It is the responsibility of the user to provide the right parameters as the user is familiar with the input code's logic and its dependencies.

## Getting Started

### Prerequisites

First, clone the ComPar code provided here.
Then, you should install and load the supported compilers (i.e. Cetus, Par4All and AutoPar) to your environment, as well as Python3.

### Know Your Flags

**Required Flags:**
* -wd (or --working_directory): Specify the working directory path to your code.
* -dir (or --input_dir): Specify the path to the directory of your input files.
* -main_file_r_p (or --main_file_rel_path): Main C file name relative path.
  * Default="".

**Optional Flags:**
* -comp (or --binary_compiler_type): Specify the binary compiler type.
  * Default="".
* -comp_v (or --binary_compiler_version): Specify the vesion of the binary compiler.
  * Default=None.
* -comp_f (or --binary_compiler_flags): Specify the binary compiler flags.
  * Default=None.
* -save_folders (or --delete_combinations_folders): Save all combinations folders.
                        action='store_false')
    parser.add_argument('-make', '--is_make_file', help='Use makefile flag', action='store_true')
* -make_c (or --makefile_commands): Makefile commands.
  * Default=None.
* -make_op (or --makefile_exe_folder_rel_path): Makefile output executable folder relative path to input directory.
  * Default="".
* -make_on (or --makefile_output_exe_file_name): Makefile output executable file name.
  * Default="".
* -ignore (or --ignored_rel_path): List of relative folder paths to be ignored while parallelizing.
  * Default=None.
* -p4a_f (or --par4all_flags): List of Par4all flags.
  * Default=None.
* -autopar_f (or --autopar_flags): List of Autopar flags.
  * Default=None.
* -cetus_f (or --cetus_flags): List of Cetus flags.
  * Default=None.
* -include (or --include_dirs_list): Include dir names for compilation - relative paths.
  * Default=None.
* -main_file_p (or --main_file_parameters): List of main C file parameters.
  * Default=None.
* -slurm_p (or --slurm_parameters): List of SLURM parameters.
  * Default=None.
    parser.add_argument('-nas', '--is_nas', help='Is NAS Benchmark', action='store_true')
* -t (or --time_limit): Time limit for runtime execution.
  * Default=None.
    
```
d
```
