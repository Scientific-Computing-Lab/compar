import subprocess
import os


def run_subprocess(command, cwd=os.curdir):
    if isinstance(command, list):
        command = " ".join(command)
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=True,
                             env=os.environ)
    std_out, std_err = pipes.communicate()
    return_code = pipes.returncode
    pipes.kill()
    del pipes
    std_out, std_err = str(std_out, encoding='utf-8'), str(std_err, encoding='utf-8')
    return std_out, std_err, return_code
