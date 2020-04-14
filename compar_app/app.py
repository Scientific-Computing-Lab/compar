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
    return render_template('single-file-mode.html', form=form)


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
    form = SingleFileForm(request.form)
    print(form.validate_on_submit())
    print(form.errors)
    print(request.files)
    if form.validate_on_submit():
        DATA['slurm_parameters'] = form.slurm_parameters.data
        DATA['save_combinations'] = form.save_combinations.data
        DATA['compiler'] = form.compiler.data
        DATA['compiler_version'] = form.compiler_version.data
        DATA['compiler_flags'] = form.compiler_flags.data
        DATA['source_file_text'] = form.source_file_code.data
        # print("blabla", DATA)
        # print("test codemirror: ", form.source_file_code.data)
        # handling upload file/paste code
        if form.source_file_code.data:
            file = form.upload_file.data
            print("file test: ", file)
            if file:
                DATA['source_file_name'] = file.filename
            else:
                DATA['source_file_name'] = 'source_file.c'
            # print(DATA['source_file_path'], form.source_file_area.data)
            # check for now because filefield is not part of the field
            if not DATA['source_file_name']:
                DATA['source_file_name'] = 'source_file.c'
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
        print("result_file: " + str(DATA))
        result_file = os.path.join(SOURCE_FILE_DIRECTORY, DATA['source_file_name'])
        text = ''
        with open(result_file) as fp:
            text = fp.read()
        return jsonify({"text":text})


if __name__ == "__main__":
    app.debug = True
    app.run(port=4444)