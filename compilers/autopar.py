import argparse
import os
import subprocess
import distutils
import time
from compiler import Compiler

class Autopar(Compiler):

    def __init__(self,version,input_filename,output_filename,compilation_flags):
        Compiler.__init__(self,version,input_filename,output_filename,compilation_flags)

    def compile(self):

        # Parallelizing
        try:
            dir = os.path.abspath(self.get_input_filename())
            # dir_name = os.path.basename(dir)
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if os.path.splitext(name)[1] == '.c':
                        print(name, dir)
                        self.run_autopar(name, dir, self.get_compilation_flags())
            return True
        except Exception as e:
            print("files in directory " + self.get_input_filename() + " failed to be parallel!")
            print(e)
            return False

    def run_autopar(self, f_name, dest_dir, options):
        print ("Parallelizing "+ f_name)
        #sub_proc = subprocess.Popen(['autoPar'] + options + [f_name, f_name], cwd=dest_dir)
        #sub_proc.wait()
        print ("Done parallel work")

x= Autopar(3,"dass","sdfdsf",["www"]).compile()