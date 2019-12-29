from compiler import Compiler
import os
import subprocess

class icc(Compiler):

    def __init__(self, version, compilation_flags, input_file_directory, output_file_directory=None):
        Compiler.__init__(self, version, compilation_flags, input_file_directory, output_file_directory)

    def compile(self):

        pass
