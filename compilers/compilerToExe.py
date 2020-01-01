from compiler import Compiler
import os
import subprocess


class CompilerToExe(Compiler):

    def __init__(self, compiler_name, version, compilation_flags, input_file_directory, output_file_directory=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)
        self._compiler_name = compiler_name

    def get_compiler_name(self):
        return self._compiler_name

    def set_compiler_name(self, compiler_name):
        self._compiler_name = compiler_name

    def compile(self):
        success = False

        # Compiling
        try:
            dir = os.path.abspath(self.get_input_file_directory())
            # dir_name = os.path.basename(dir)
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        process_code = self.run_compiler(name, dir, self.get_compilation_flags())
                        if process_code == 0:
                            print("Compiling " + name)
                            success = True

            if not success:
                raise Exception("Failed To Compile!")

            print("Done Compile work")
            return True

        except Exception as e:
            print("files in directory " + self.get_input_file_directory() + " failed to be compiled!")
            print(e)
            return False

    def run_compiler(self, file_name, file_dir, options):
        if options in ["", None]:
            options = []
        try:
            sub_proc = subprocess.Popen([self.get_compiler_name()]+ ["-fopenmp"] + options + [file_name] +
                                    ["-o" + " " + file_name+".x"], cwd=file_dir, stderr=subprocess.DEVNULL)
            sub_proc.wait()

            return sub_proc.returncode

        except Exception as e:
            pass

