from parallelCompiler import ParallelCompiler
import subprocess
import os


class Cetus(ParallelCompiler):

    def __init__(self, version, input_file_directory=None, compilation_flags=None, file_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)

    def compile(self):
        super().compile()
        try:
            for file in self.get_file_list():
                cwd_path = os.path.dirname(file["file_full_path"])
                sub_proc = subprocess.Popen(['cetus'] + self.get_compilation_flags() + [file["file_name"]], cwd=cwd_path)
                sub_proc.wait()
            return True

        except Exception as e:
            print("files in directory " + self.get_input_filename_directory() + " failed to be parallel!")
            print(e)
            return False