import os
import subprocess
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Start Compar':
            # TODO-open compar object
            # TODO - get args from may to compr
            makefile = False  # TODO - set it from May page
            command = ["python3 test.py"]  # TODO- change to compar commend
            output = ""
            compar_process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            for line in compar_process.stdout:  # (if compar_process.poll != None:)
                output += line
            compar_process.stdout.close()
            return_code = compar_process.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, command)

            if makefile:
                result_file = "main/diretcory"  # TODO- change it to the real directory  location
                #TODO - create line numbering for makefile as well
            else:
                result_file = ""
                result_lines = ""
                num_of_lines = 1
                f = open("test.py", "r") #  TODO - change it to the real file location
                for line in f:
                    result_lines += str(num_of_lines) + " "
                    num_of_lines = num_of_lines + 1
                    result_file += line
                f.close()
            print()
            print(output)
            return redirect(url_for('result', result_file=result_file, result_lines=result_lines,  output=output))
    else:
        return render_template("output.html")


@app.route('/result')
def result():
    return render_template('result.html',
                           result_file=request.args.get('result_file'),
                           output=request.args.get('output'),result_lines=request.args.get('result_lines'))


if __name__ == "__main__":
    app.run(debug=True)

