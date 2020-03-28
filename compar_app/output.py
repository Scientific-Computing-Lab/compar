import subprocess
from time import sleep
from flask import Flask, render_template

app = Flask(__name__)
output_log = ""


@app.route('/')
def index():
    # render the template (below) that will use JavaScript to read the stream
    return render_template('progress.html')


@app.route('/stream_progress')
def stream():
    def generate():
        global output_log
        proc = subprocess.Popen(['python -u test.py'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            output_log += str(line) + "\n"
            yield line.rstrip() + b'\n'
        sleep(5)

    return app.response_class(generate(), mimetype='text/plain')


@app.route('/results')
def results():
    # TODO: take from MAY
    is_copy_paste = True

    if is_copy_paste:
        result_file = ""
        result_lines = ""
        num_of_lines = 1
        # TODO - change it to the real file location
        final_code_path = "test2.py"
        with open(final_code_path, "r") as f:
            for line in f:
                result_lines += str(num_of_lines) + " "
                num_of_lines = num_of_lines + 1
                result_file += line
        return render_template('result.html', result_file=result_file, output=output_log, result_lines=result_lines)
    else:
        # TODO: show link to working dir
        result_file = "main/diretcory"
        # TODO: render template of new page
        return "asd"


if __name__ == "__main__":
    app.run(debug=True, port=6060)

