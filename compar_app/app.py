import os
import sys

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
import subprocess
from flask import request, jsonify
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

DATA = {}
SOURCE_FILE_DIRECTORY = 'temp'
SOURCE_FILE_NAME = 'temp_source_file.c'
SOURCE_FILE_PATH = os.path.join(SOURCE_FILE_DIRECTORY, SOURCE_FILE_NAME)
SOURCE_FILE_PATH_REL_TO_TEMPLATE = os.path.join("..", SOURCE_FILE_DIRECTORY, SOURCE_FILE_NAME)


class SingleFileForm(FlaskForm):
    slurm_parameters = TextAreaField('slurm_parameters', validators=[InputRequired()])
    save_combinations = BooleanField('save_combinations')
    compiler = SelectField('compiler', choices=[('icc', 'ICC'), ('gcc', 'GCC')])
    compiler_version = StringField('compiler_version')
    compiler_flags = TextAreaField('compiler_flags')
    source_file_code = TextAreaField('source_file_code')
    upload_file = FileField('upload_file', validators=[FileAllowed(['c'], 'c file only!')])  # valiation dont work
    result_file_area = TextAreaField('result_file_area')


@app.route("/")
@app.route("/singlefile", methods=['GET', 'POST'])
def single_file():
    form = SingleFileForm(request.form)
    return render_template('single-file-mode.html', form=form, source_file_path=SOURCE_FILE_PATH_REL_TO_TEMPLATE)


@app.route('/multiplefiles')
def multiple_files():
    return render_template('multiple-files-mode.html')


@app.route('/makefile')
def makefile():
    return render_template('makefile-mode.html')


def save_source_file(file_name, txt):
    if not os.path.exists(SOURCE_FILE_DIRECTORY):
        os.mkdir(SOURCE_FILE_DIRECTORY)
    file_path = os.path.join(SOURCE_FILE_DIRECTORY, file_name)
    with open(file_path, "w") as f:
        f.write(txt)


@app.route('/something/', methods=['post'])
def something():
    global DATA
    form = SingleFileForm(request.form)
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        DATA = dict(form.data)

        # handling upload file/paste code
        if form.source_file_code.data:
            try:
                if request.files and request.files['upload_file'].filename != "":
                    # special handling for uploaded files will be here
                    print("file test: ", request.files['upload_file'].filename)
                else:
                    pass
            except Exception as e:
                pass
            finally:
                DATA['source_file_name'] = SOURCE_FILE_NAME
            save_source_file(file_name=DATA['source_file_name'], txt=form.source_file_code.data)
        return jsonify(data={'message': 'hello {}'.format(form.slurm_parameters.data)})
    return jsonify(errors=form.errors)


@app.route('/stream_progress')
def stream():
    # TODO: add check in the BE in case compar is ruuning do nothing
    def generate():
        compar_file = r"../program.py"
        compar_file = "testt.py"
        interpreter = sys.executable
        command = [interpreter, '-u', compar_file]
        proc = subprocess.Popen(" ".join(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            yield line.rstrip() + b'\n'
        # TODO - Get the source file !
    return app.response_class(generate(), mimetype='text/plain')


@app.route('/result_file', methods=['get'])
def result_file():
    result_file_path = os.path.join(SOURCE_FILE_DIRECTORY, DATA['source_file_name'])
    result_file_file_code = ''
    with open(result_file_path) as fp:
        result_file_file_code = fp.read()
    return jsonify({"text": result_file_file_code})


if __name__ == "__main__":
    app.debug = True
    app.run(port=4444)