import os
import re

def test_output(working_dir: str, output_file_name: str):
    test_output_nas(working_dir, output_file_name)
    # assert True


def test_output_nas(working_dir: str, output_file_name: str):
    with open(os.path.join(working_dir, output_file_name)) as f:
        output = f.read().lower()
        regexp = re.compile(r'verification\s+=?\s*successful')
        success = regexp.search(output)
        assert success



# if __name__ == "__main__":
#     test_output(working_dir='/home/idanmos/projects/auto_parallel/nas/compar_nas_res/ep/combinations/serial',output_file_name='serial.log')
