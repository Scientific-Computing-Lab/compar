import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,BooleanField,SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
import subprocess
from flask import request
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

DATA = {}
output_log = ""

class singleFileForm(FlaskForm):
    slurm_parameters = TextAreaField('slurm_parameters', validators=[InputRequired()])
    save_combinations = BooleanField('save_combinations')
    compiler = SelectField('compiler', choices=[('icc', 'ICC'), ('gcc','GCC')])
    compiler_version = StringField('compiler_version')
    compiler_flags = TextAreaField('compiler_flags')



@app.route("/")
@app.route("/singlefile", methods=['GET', 'POST'])
def single_file():
    form = singleFileForm(request.form)

    if request.method == "POST" and form.validate_on_submit():
        print("blabla",form.slurm_parameters.data, form.save_combinations.data, form.compiler.data, form.compiler_version.data, form.compiler_flags.data)
        return render_template('single-file-mode.html', form=form)
    print(form.slurm_parameters.errors)
    return render_template('single-file-mode.html', form=form)

@app.route('/multiplefiles')
def multiple_files():
    return render_template('multiple-files-mode.html')

@app.route('/makefile')
def makefile():
    return render_template('makefile-mode.html')


@app.route('/stream_progress')
def stream():
    def generate():
        global output_log
        compar_file = "testt.py"
        proc = subprocess.Popen([f'python3 -u {compar_file}'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            output_log += str(line) + "\n"
            yield line.rstrip() + b'\n'
    return app.response_class(generate(), mimetype='text/plain')


if __name__ == "__main__":
    app.debug = True
    app.run()