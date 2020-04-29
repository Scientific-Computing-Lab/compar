import subprocess
import os
import logger


def run_subprocess(command: list or str, cwd: str = os.curdir):
    if isinstance(command, list):
        command = " ".join(command)
    logger.verbose(f'Running {command} command')
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=True,
                             env=os.environ, universal_newlines=True)
    std_out, std_err = pipes.communicate()
    return_code = pipes.returncode
    pipes.kill()
    del pipes
    if return_code != 0:
        raise subprocess.CalledProcessError(cmd=command, output=std_out, stderr=std_err, returncode=return_code)
    return std_out, std_err, return_code
