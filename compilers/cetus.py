from compilers.parallelCompiler import ParallelCompiler
import subprocess
import shutil
import os


class Cetus(ParallelCompiler):

    def __init__(self, version, input_file_directory=None, compilation_flags=None, file_list=None):
        super().__init__(version, compilation_flags, input_file_directory, file_list)

    def compile(self):
        super().compile()
        try:
            for file in self.get_file_list():
                cwd_path = os.path.dirname(file["file_full_path"])
                subprocess.run([' cetus {} {}'.format(" ".join(self.get_compilation_flags()), file["file_name"])],
                               shell=True, cwd=cwd_path)
                # Replace file from cetus output folder into original file folder
                if os.path.isdir(os.path.join(cwd_path, "cetus_output")):
                    src_file = os.path.join(cwd_path, "cetus_output", file["file_name"])
                    dst_file = file["file_full_path"]
                    shutil.copy(src_file, dst_file)
                    shutil.rmtree(os.path.join(cwd_path, "cetus_output"))
            return True

        except Exception as e:
            print("files in directory " + self.get_input_filename_directory() + " failed to be parallel!")
            print(e)
            return False
