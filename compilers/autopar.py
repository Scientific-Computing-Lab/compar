import subprocess
from compiler import Compiler

class Autopar(Compiler):

    autopar_script_path = "scripts/autoPar_script.py"

    def __init__(self,version,input_filename,output_filename,compilation_flags):
        Compiler.__init__(self,version,input_filename,output_filename,compilation_flags)

    def compile(self):

        # Parallelizing
        try:
            process = subprocess.Popen(['bash','-c', "python3" + Autopar.autopar_script_path + "-dir " + self.get_input_filename() + " -options " + " ".join(str(x) for x in self.get_compilation_flags()) ])
            process.wait()
            return True
        except:
            print("files in directory " + self.get_input_filename() + " failed to be parallel!")
            return False

