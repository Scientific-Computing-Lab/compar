import os
import sys
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from werkzeug.exceptions import abort
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import InputRequired, ValidationError
from flask_bootstrap import Bootstrap
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
import subprocess
from flask import request, jsonify, Response, session, stream_with_context, send_from_directory
from flask import Flask, render_template
from datetime import datetime
import hashlib
import getpass
import shutil


app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

TEMP_FILES_DIRECTORY = 'temp'
COMPAR_PROGRAM_FILE = 'program.py'
GUI_DIR_NAME = 'GUI'
SINGLE_FILE_MODE = 'single-file-mode'
MULTIPLE_FILES_MODE = 'multiple-files-mode'
MAKEFILE_MODE = 'makefile-mode'


def path_validator(form, field):
    if field.data and not os.path.exists(field.data):
        raise ValidationError('Path is invalid')


def relative_path_validator(form, field):
    if not form.input_directory.data or not os.path.exists(os.path.join(form.input_directory.data, field.data)):
        raise ValidationError('Relative path is invalid')


class SingleFileForm(FlaskForm):
    compiler_flags = StringField('compiler_flags')
    compiler_version = StringField('compiler_version')
    slurm_partition = StringField('slurm_partition', validators=[InputRequired()], default='grid')
    save_combinations = BooleanField('save_combinations')
    clear_database = BooleanField('clear_database')
    with_markers = BooleanField('with_markers')
    slurm_parameters = StringField('slurm_parameters')
    jobs_count = h5fields.IntegerField('jobs_count', widget=h5widgets.NumberInput(min=0, max=100, step=1),
                                       validators=[InputRequired()], default=4)
    days_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=100, step=1), default=0)
    hours_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=23, step=1), default=0)
    minutes_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    seconds_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    main_file_parameters = StringField('main_file_parameters')
    compiler = SelectField('compiler', choices=[('gcc', 'GCC'), ('icc', 'ICC')])
    source_file_code = TextAreaField('source_file_code', validators=[InputRequired()])
    upload_file = FileField('upload_file', validators=[FileAllowed(['c'], 'Only C files allowed!')])
    result_file_area = TextAreaField('result_file_area')
    log_level = SelectField('compiler', choices=[('', 'Basic'), ('verbose', 'Verbose'), ('debug', 'Debug')])
    test_path = StringField('test_file_path', validators=[path_validator])
    compar_mode = SelectField('mode', choices=[('override', 'Override'), ('new', 'New'), ('continue', 'Continue')])


class MultipleFilesForm(FlaskForm):
    input_directory = StringField('input_directory', validators=[path_validator, InputRequired()])
    output_directory = StringField('output_directory', validators=[InputRequired()])
    main_file_path = StringField('main_file_path', validators=[relative_path_validator, InputRequired()])
    compiler_flags = StringField('compiler_flags')
    compiler_version = StringField('compiler_version')
    slurm_partition = StringField('slurm_partition', validators=[InputRequired()], default='grid')
    save_combinations = BooleanField('save_combinations')
    clear_database = BooleanField('clear_database')
    with_markers = BooleanField('with_markers')
    slurm_parameters = StringField('slurm_parameters')
    jobs_count = h5fields.IntegerField('jobs_count', widget=h5widgets.NumberInput(min=0, max=100, step=1),
                                       validators=[InputRequired()], default=4)
    days_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=100, step=1), default=0)
    hours_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=23, step=1), default=0)
    minutes_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    seconds_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    main_file_parameters = StringField('main_file_parameters')
    compiler = SelectField('compiler', choices=[('gcc', 'GCC'), ('icc', 'ICC')])
    log_level = SelectField('compiler', choices=[('', 'Basic'), ('verbose', 'Verbose'), ('debug', 'Debug')])
    test_path = StringField('test_file_path', validators=[path_validator])
    compar_mode = SelectField('mode', choices=[('override', 'Override'), ('new', 'New'), ('continue', 'Continue')])


class MakefileForm(FlaskForm):
    input_directory = StringField('input_directory', validators=[path_validator, InputRequired()])
    output_directory = StringField('output_directory', validators=[InputRequired()])
    main_file_path = StringField('main_file_path', validators=[relative_path_validator, InputRequired()])
    makefile_commands = StringField('makefile_commands', validators=[InputRequired()])
    executable_path = StringField('executable_path', validators=[relative_path_validator])
    executable_file_name = StringField('executable_file_name', validators=[InputRequired()])
    ignore_folder_paths = StringField('ignore_folder_paths')
    include_folder_paths = StringField('include_folder_paths')
    extra_files_paths = StringField('extra_files_paths')
    slurm_partition = StringField('slurm_partition', validators=[InputRequired()], default='grid')
    save_combinations = BooleanField('save_combinations')
    clear_database = BooleanField('clear_database')
    with_markers = BooleanField('with_markers')
    slurm_parameters = StringField('slurm_parameters')
    jobs_count = h5fields.IntegerField('jobs_count', widget=h5widgets.NumberInput(min=0, max=100, step=1),
                                       validators=[InputRequired()], default=4)
    days_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=100, step=1), default=0)
    hours_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=23, step=1), default=0)
    minutes_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    seconds_field = h5fields.IntegerField(widget=h5widgets.NumberInput(min=0, max=59, step=1), default=0)
    main_file_parameters = StringField('main_file_parameters')
    log_level = SelectField('compiler', choices=[('', 'Basic'), ('verbose', 'Verbose'), ('debug', 'Debug')])
    test_path = StringField('test_file_path', validators=[path_validator])
    compar_mode = SelectField('mode', choices=[('override', 'Override'), ('new', 'New'), ('continue', 'Continue')])


@app.route("/")
@app.route("/singlefile", methods=['GET', 'POST'])
def single_file():
    form = SingleFileForm(request.form)
    return render_template('single-file-mode.html', form=form)


@app.route('/multiplefiles', methods=['GET', 'POST'])
def multiple_files():
    form = MultipleFilesForm(request.form)
    return render_template('multiple-files-mode.html', form=form)


@app.route('/makefile', methods=['GET', 'POST'])
def makefile():
    form = MakefileForm(request.form)
    return render_template('makefile-mode.html', form=form)


@app.route('/single_file_submit', methods=['post'])
def single_file_submit():
    form = SingleFileForm()
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
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
                guid = getpass.getuser() + str(datetime.now())
                file_hash = f"temp_{hashlib.sha3_256(guid.encode()).hexdigest()}"
                # create input dir
                input_dir_path = os.path.join(TEMP_FILES_DIRECTORY, file_hash)
                os.makedirs(input_dir_path, exist_ok=True)
                current_dir_path = os.path.dirname(os.path.realpath(__file__))
                session['input_dir'] = os.path.join(current_dir_path, input_dir_path)
                source_file_name = f"{file_hash}.c"
                source_file_path = os.path.join(input_dir_path, source_file_name)
                save_source_file(file_path=source_file_path, txt=form.source_file_code.data)
                # create working dir
                working_dir_path = os.path.join(TEMP_FILES_DIRECTORY, f"{file_hash}_wd")
                os.makedirs(working_dir_path, exist_ok=True)
                session['working_dir'] = os.path.join(current_dir_path, working_dir_path)
                # update main file rel path as filename
                session['main_file_rel_path'] = source_file_name
                # other fields
                session['compiler'] = form.compiler.data
                session['save_combinations'] = form.save_combinations.data
                session['clear_database'] = form.clear_database.data
                session['with_markers'] = form.with_markers.data
                session['main_file_parameters'] = form.main_file_parameters.data
                session['compiler_flags'] = form.compiler_flags.data
                session['compiler_version'] = form.compiler_version.data
                session['slurm_parameters'] = form.slurm_parameters.data
                session['slurm_partition'] = form.slurm_partition.data
                session['job_count'] = form.jobs_count.data
                session['log_level'] = form.log_level.data
                session['test_path'] = form.test_path.data
                session['time_limit'] = handle_time_limit(form.days_field.data, form.hours_field.data,
                                                          form.minutes_field.data, form.seconds_field.data)
                session['compar_mode'] = form.compar_mode.data
        else:
            return jsonify(errors=form.errors)
        return jsonify(data={'message': 'The form is valid.'})
    return jsonify(errors=form.errors)


@app.route('/multiple_files_submit', methods=['post'])
def multiple_files_submit():
    form = MultipleFilesForm()
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        session['input_dir'] = form.input_directory.data
        session['working_dir'] = form.output_directory.data
        os.makedirs(session['working_dir'], exist_ok=True)
        session['main_file_rel_path'] = form.main_file_path.data
        # other fields
        session['compiler'] = form.compiler.data
        session['save_combinations'] = form.save_combinations.data
        session['clear_database'] = form.clear_database.data
        session['with_markers'] = form.with_markers.data
        session['main_file_parameters'] = form.main_file_parameters.data
        session['compiler_flags'] = form.compiler_flags.data
        session['compiler_version'] = form.compiler_version.data
        session['slurm_parameters'] = form.slurm_parameters.data
        session['slurm_partition'] = form.slurm_partition.data
        session['job_count'] = form.jobs_count.data
        session['log_level'] = form.log_level.data
        session['test_path'] = form.test_path.data
        session['time_limit'] = handle_time_limit(form.days_field.data, form.hours_field.data,
                                                  form.minutes_field.data, form.seconds_field.data)
        session['compar_mode'] = form.compar_mode.data
        return jsonify(data={'message': 'The form is valid.'})
    return jsonify(errors=form.errors)


@app.route('/makefile_submit', methods=['post'])
def makefile_submit():
    form = MakefileForm()
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        session['input_dir'] = form.input_directory.data
        session['working_dir'] = form.output_directory.data
        os.makedirs(session['working_dir'], exist_ok=True)
        session['main_file_rel_path'] = form.main_file_path.data
        # other fields
        session['makefile_commands'] = form.makefile_commands.data
        session['executable_path'] = form.executable_path.data
        session['executable_file_name'] = form.executable_file_name.data
        session['ignore_folder_paths'] = form.ignore_folder_paths.data
        session['include_folder_paths'] = form.include_folder_paths.data
        session['extra_files_paths'] = form.extra_files_paths.data
        session['save_combinations'] = form.save_combinations.data
        session['clear_database'] = form.clear_database.data
        session['with_markers'] = form.with_markers.data
        session['main_file_parameters'] = form.main_file_parameters.data
        session['slurm_parameters'] = form.slurm_parameters.data
        session['slurm_partition'] = form.slurm_partition.data
        session['job_count'] = form.jobs_count.data
        session['log_level'] = form.log_level.data
        session['test_path'] = form.test_path.data
        session['time_limit'] = handle_time_limit(form.days_field.data, form.hours_field.data,
                                                  form.minutes_field.data, form.seconds_field.data)
        session['compar_mode'] = form.compar_mode.data
        return jsonify(data={'message': 'The form is valid.'})
    return jsonify(errors=form.errors)


@app.route('/stream_progress', methods=['POST'])
def stream():
    compar_command = ''
    compar_mode = ''
    data = request.get_json()
    if 'mode' not in data.keys():
        abort(400, "Cannot initiate Compar without mode been specified.")
    else:
        compar_mode = data['mode']
    if compar_mode in [SINGLE_FILE_MODE, MULTIPLE_FILES_MODE]:
        compar_command = generate_compar_command_without_makefile()
    elif compar_mode == MAKEFILE_MODE:
        compar_command = generate_compar_command_with_makefile()
    else:
        abort(400, f"Cannot initiate Compar with mode: {compar_mode}.")

    def generate():
        compar_file = COMPAR_PROGRAM_FILE
        interpreter = sys.executable
        command = [interpreter, '-u', compar_file, compar_command]
        print(command)
        proc = subprocess.Popen(" ".join(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                cwd='../')
        for line in proc.stdout:
            yield line.rstrip() + b'\n'
        proc.communicate()[0]
        return_code = proc.returncode
        session['return_code'] = return_code
    return Response(stream_with_context(generate()))


@app.route('/result_file', methods=['get'])
def result_file():
    result_file_path = os.path.join(session['working_dir'], 'final_results', session['main_file_rel_path'])
    return_code = session.get('return_code')
    if return_code is None:
        return_code = 0
    if return_code != 0 or not os.path.exists(os.path.dirname(result_file_path)) or not os.path.exists(
            result_file_path):
        return jsonify({"text": "Compar failed. Check the output log for more information."})
    with open(result_file_path) as fp:
        result_file_code = fp.read()
    return jsonify({"text": result_file_code})


@app.route('/downloadResultFile', methods=['get'])
def download_result_file():
    result_file_path = os.path.join(session['working_dir'], 'final_results', session['main_file_rel_path'])
    with open(result_file_path, 'r') as fp:
        result_code = fp.read()
    return Response(
        result_code,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=Compar_results.c"}
    )


@app.route('/showFilesStructure', methods=['get'])
def show_files_structure():
    result_file_path = os.path.join(session['working_dir'], 'final_results')
    return_code = session.get('return_code')
    if return_code is None:
        return_code = 0
    if return_code != 0 or not os.path.exists(os.path.dirname(result_file_path)) or not os.path.exists(
            result_file_path):
        return jsonify({"success": 0, "text": "Compar failed.\nCheck the output log for more information."})
    return jsonify({"success": 1,
                    "text": f"Compar successfully finished.\nResults can be found at the following directory:",
                    "path": result_file_path})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def generate_compar_command_without_makefile():
    command = []
    # input dir
    command += [f"-dir {session['input_dir']}"]
    # working dir
    command += [f"-wd {session['working_dir']}"]
    # main file rel path
    command += [f"-main_file_r_p {session['main_file_rel_path']}"]
    # compiler type
    command += [f"-comp {session['compiler']}"]
    # save combinations
    if session['save_combinations']:
        command += [f"-save_folders"]
    # main file parameters
    if session['main_file_parameters']:
        command += [f"-main_file_p {session['main_file_parameters']}"]
    # compiler flags
    if session['compiler_flags']:
        command += [f"-comp_f {session['compiler_flags']}"]
    # compiler version
    if session['compiler_version']:
        command += [f"-comp_v {session['compiler_version']}"]
    # slurm_parameters
    if session['slurm_parameters']:
        command += [f"-slurm_p {session['slurm_parameters']}"]
    # slurm partition
    if session['slurm_partition']:
        command += [f"-partition {session['slurm_partition']}"]
    # job count
    if session['job_count']:
        command += [f"-jobs_quantity {session['job_count']}"]
    # log level
    if session['log_level'] and session['log_level'] != 'basic':
        level = ""
        if session['log_level'] == 'verbose':
            level = "v"
        elif session['log_level'] == 'debug':
            level = "vv"
        command += [f"-{level}"]
    # test file path
    if session['test_path']:
        command += [f"-test_file {session['test_path']}"]
    # time limit
    if session['time_limit']:
        command += [f"-t {session['time_limit']}"]
    # clear database
    if session['clear_database']:
        command += [f"-clear_db"]
    # with markers
    if session['with_markers']:
        command += [f"-with_markers"]
    # compar_mode
    if session['compar_mode']:
        command += [f"-mode {session['compar_mode']}"]
    return ' '.join(command)


def generate_compar_command_with_makefile():
    command = []
    # input dir
    command += [f"-dir {session['input_dir']}"]
    # working dir
    command += [f"-wd {session['working_dir']}"]
    # main file rel path
    command += [f"-main_file_r_p {session['main_file_rel_path']}"]
    # makefile commands
    command += [f"-make"]
    command += [f"-make_c {session['makefile_commands']}"]
    # executable path
    command += [f"-make_op {session['executable_path']}"]
    # executable file name
    command += [f"-make_on {session['executable_file_name']}"]
    # folders to ignore
    if session['ignore_folder_paths']:
        command += [f"-ignore {session['ignore_folder_paths']}"]
    # folders to include
    if session['include_folder_paths']:
        command += [f"-include {session['include_folder_paths']}"]
    # extra files to include (mainly used by Par4all)
    if session['extra_files_paths']:
        command += [f"-extra {session['extra_files_paths']}"]
    # save combinations
    if session['save_combinations']:
        command += [f"-save_folders"]
    # main file parameters
    if session['main_file_parameters']:
        command += [f"-main_file_p {session['main_file_parameters']}"]
    # slurm_parameters
    if session['slurm_parameters']:
        command += [f"-slurm_p {session['slurm_parameters']}"]
    # slurm partition
    if session['slurm_partition']:
        command += [f"-partition {session['slurm_partition']}"]
    # job count
    if session['job_count']:
        command += [f"-jobs_quantity {session['job_count']}"]
    # log level
    if session['log_level'] and session['log_level'] != 'basic':
        level = ""
        if session['log_level'] == 'verbose':
            level = "v"
        elif session['log_level'] == 'debug':
            level = "vv"
        command += [f"-{level}"]
    # test file path
    if session['test_path']:
        command += [f"-test_file {session['test_path']}"]
    # time limit
    if session['time_limit']:
        command += [f"-t {session['time_limit']}"]
    # clear database
    if session['clear_database']:
        command += [f"-clear_db"]
    # with markers
    if session['with_markers']:
        command += [f"-with_markers"]
    # compar_mode
    if session['compar_mode']:
        command += [f"-mode {session['compar_mode']}"]
    return ' '.join(command)


def handle_time_limit(days, hours, minutes, seconds):
    time_limit = ''
    if days or hours or minutes or seconds:
        time_limit = f"{str(hours)}:{str(minutes)}:{str(seconds)}"
    if days:
        time_limit = f"{str(days)}-" + time_limit
    return time_limit


def clean_temp_files():
    if os.path.exists(TEMP_FILES_DIRECTORY):
        shutil.rmtree(TEMP_FILES_DIRECTORY)


def save_source_file(file_path, txt):
    with open(file_path, "w") as f:
        f.write(txt)


if __name__ == "__main__":
    clean_temp_files()
    app.debug = True
    app.run(port=4445)
