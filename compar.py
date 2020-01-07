import os
import subprocess
from compilers.autopar import Autopar
from compilers.cetus import Cetus
from compilers.par4all import Par4all


class Compar:

    def __init__(self,
                 working_directory,
                 input_dir,
                 binary_compiler_type,
                 makefile_name="",
                 makefile_parameters=[],
                 makefile_output_files="",
                 is_make_file=False,
                 binary_compiler_flags="",
                 par4all_flags="",
                 autopar_flags="",
                 cetus_flags="",
                 main_file_name="",
                 main_file_parameters="",
                 slurm_parameters=""):

        #Build compar environment-----------------------------------
        self.working_directory = working_directory
        self.backup_files_dir = working_directory + "/backup"
        self.original_files_dir = working_directory + "/original_files"
        self.combinations_dir = working_directory + "/combinations"
        self.__build_compar_work_environment(input_dir)
        #-----------------------------------------------------------

        #Creating compiler variables----------------------------------
        # TODO -fix varsion
        version = ""  # dont know if geting this from the user
        self.c_files_list = Compar.make_c_file_list(self.original_files_dir)
        self.binary_compiler_type = binary_compiler_type
        self.par4all_compiler = Par4all(version, par4all_flags, self.original_files_dir, self.c_files_list)
        self.autopar_compiler = Autopar(version, autopar_flags, self.original_files_dir, self.c_files_list)
        self.cetus_compiler = Cetus(version, cetus_flags, self.original_files_dir, self.c_files_list)
        #-----------------------------------------------------------

        #Saves compiler flags---------------------------------------
        self.user_par4all_flags = par4all_flags
        self.user_autopar_flags = autopar_flags
        self.user_cetus_flags = cetus_flags
        self.user_binary_compiler_flags = binary_compiler_flags
        #-----------------------------------------------------------

        #Makefile---------------------------------------------------
        self.is_make_file = is_make_file
        self.makefile_name = makefile_name
        self.makefile_parameters = makefile_parameters
        self.makefile_output_files = makefile_output_files
        #-----------------------------------------------------------

        #Main file--------------------------------------------------
        self.main_file_name = main_file_name
        self.main_file_parameters = main_file_parameters
        # ----------------------------------------------------------

        #SLURM------------------------------------------------------
        self.slurm_parameters = slurm_parameters
        # ----------------------------------------------------------

    def __build_compar_work_environment(self, input_dir):
        os.makedirs(self.original_files_dir, exist_ok=True)
        os.makedirs(self.combinations_dir, exist_ok=True)
        os.makedirs(self.backup_files_dir, exist_ok=True)

        if os.path.isdir(input_dir):
            cmd="cp -r {0}/* {1} ".format(input_dir, self.original_files_dir)
            subprocess.check_output(cmd, shell=True)
            cmd = "cp -r {0}/* {1} ".format(input_dir, self.backup_files_dir)
            subprocess.check_output(cmd, shell=True)
        else:
            cmd = "cp -r {0} {1} ".format(input_dir, self.original_files_dir)
            subprocess.check_output(cmd, shell=True)
            cmd = "cp -r {0} {1} ".format(input_dir, self.backup_files_dir)
            subprocess.check_output(cmd, shell=True)

    @staticmethod
    def make_c_file_list(input_dir):
        files_list = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.c':
                    files_list.append({"file_name": os.path.basename(file), "file_full_path": os.path.abspath(file)})

        return files_list
