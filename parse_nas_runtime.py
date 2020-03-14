import os
import re
import json
from argparse import ArgumentParser


def parse(container_dir):
    results = []
    for path, dirs, files in os.walk(container_dir):
        file_name = os.path.basename(path) + '.log'
        for file in files:
            if file == file_name:
                full_path = os.path.join(path, file)
                combination_id = os.path.basename(os.path.dirname(full_path))
                with open(full_path, 'r') as f:
                    content = f.read()
                sec_runtime_res = re.findall(r'Time in seconds[ ]*=[ ]*\d+.\d+', content)
                if sec_runtime_res:
                    run_time = sec_runtime_res[0].split('=')[1].replace(' ', '')
                    results.append({'combination_id': combination_id,
                                    'run_time': float(run_time),
                                    'rel_path': os.path.relpath(full_path, container_dir)})
    results.insert(0, {'min': min(results, key=lambda res: res['run_time'])})
    return results


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-dir', '--container_dir', required=True)
    args = arg_parser.parse_args()

    run_time_results = parse(args.container_dir)
    with open(os.path.join(args.container_dir, 'nas_runtime_results.json'), 'w') as json_file:
        json_file.write(json.dumps(run_time_results))


if __name__ == '__main__':
    main()
