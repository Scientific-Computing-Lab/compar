import os
import subprocess
import shutil
from exceptions import MakefileError, CombinationFailure, CompilationError


class Makefile:
    def __init__(self, working_directory, exe_folder_relative_path, exe_file_name, commands):
        if not os.path.exists(working_directory):
            raise MakefileError(f'{working_directory} is not exist!')
        if len(commands) < 1:
            raise MakefileError('Makefile requires at least one command!')
        self.working_directory = working_directory
        self.exe_folder_relative_path = exe_folder_relative_path
        self.exe_file_name = exe_file_name
        self.commands = commands

    def make(self):
        try:
            self.run_makefile()
            self.move_exe_to_base_dir()
        except subprocess.CalledProcessError as ex:
            raise CombinationFailure(
                f'Makefile return with {ex.returncode} code: {str(ex)} : {ex.output} : {ex.stderr}')
        except Exception as e:
            raise CompilationError("Makefile failed \n" + str(e))

    def run_makefile(self):
        print("Running makefile")
        for command in self.commands:
            output = subprocess.check_output([command], cwd=self.working_directory)
            print(command + ' makefile output: ' + str(output))
        print("Done makefile work")

    def move_exe_to_base_dir(self):
        exe_folder_full_path = os.path.join(self.working_directory, self.exe_folder_relative_path)
        exe_path = os.path.join(exe_folder_full_path, self.exe_file_name)
        if not os.path.exists(exe_path):
            raise MakefileError(f'{exe_path} is not exist!')
        working_dir_name = os.path.basename(os.path.dirname(self.working_directory + os.path.sep))
        exe_new_name = f'{working_dir_name}.x'
        exe_type_x_path = os.path.join(exe_folder_full_path, exe_new_name)
        exe_new_path = os.path.join(self.working_directory, exe_new_name)
        os.rename(exe_path, exe_type_x_path)
        shutil.move(exe_type_x_path, exe_new_path)
        return exe_new_path
