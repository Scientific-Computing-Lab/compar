import os
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_bootstrap import Bootstrap
import subprocess
from time import sleep
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

DATA = {}
output_log = ""


class BasicComparForm(FlaskForm):
    work_dir = StringField('Path for output folder: ', validators=[DataRequired()])
    slum_params = StringField('*Slum parameters: ')
    save = RadioField('Delete all combinations folder?', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    make_file_choice = RadioField('Do you want a make file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    submit1 = SubmitField('Next')
    #TODO - Remove test button
    test = SubmitField('TEST')


class MakeFileForm(FlaskForm):
    input_dir = StringField('Path for source file directory: ', validators=[DataRequired()])
    ignore = StringField('Folder path to be ignored (rel path): ')
    include = StringField('Folder path to be included (rel path): ')
    make_commands = StringField('*Makefile Commands: ', validators=[DataRequired()])
    make_op = StringField('Output executable folder (rel path): ', validators=[DataRequired()])
    make_on = StringField('Output executable file name: ', validators=[DataRequired()])
    main_file_p = StringField('*Main c file parameters: ')
    main_file_r_p = StringField('Main c file name (rel path): ', validators=[DataRequired()])
    nas_file = RadioField('NAS file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')


class BinaryCompilerForm(FlaskForm):
    binary_comp_name = SelectField('Compiler name: ', choices=[('gcc', 'GCC'), ('icc', 'ICC')])
    binary_comp_version = StringField('Version: ')
    binary_comp_flags = StringField('Flags: ')


class CompilersForm(FlaskForm):
    p4a = StringField('*Par4All flags: ')
    autopar = StringField('*Autopar flags: ')
    cetus = StringField('*Cetus flags: ')


class ExistsCFileForm(FlaskForm):
    input_dir = StringField('Path for source file directory: ', validators=[DataRequired()])
    main_file_p = StringField('*Main c file parameters: ')
    nas_file = RadioField('NAS file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    main_file_r_p = StringField('Main c file name (rel path): ', validators=[DataRequired()])


class EditorCForm(FlaskForm):
    editor = StringField(u'Write C code', widget=TextArea())


class DoYouHaveExistsFileForm(FlaskForm):
    exists_file = RadioField('Do you want to work with exists c file or paste the code?',
                             choices=[('yes', 'Exists file'), ('no', 'Paste code')], default='yes')
    submit2 = SubmitField('Next')


class StartForm(FlaskForm):
    submit3 = SubmitField('Start')


def is_equal_to_yes(data):
    return data == 'yes'


#TODO - i add this
def open_source_file(final_code_path):
    source_file = ''
    num_of_lines = 1
    with open(final_code_path, "r") as f:
        for line in f:
            source_file += str(num_of_lines) + " "
            num_of_lines = num_of_lines + 1
            source_file += line
    DATA['source_file'] = source_file


@app.route("/", methods=["GET", "POST"])
@app.route("/compar", methods=["GET", "POST"])
def main_page():
    main_form = BasicComparForm()
    make_form = MakeFileForm()
    binary_comp_form = BinaryCompilerForm()
    comp_form = CompilersForm()
    exists_file_form = DoYouHaveExistsFileForm()
    start_form = StartForm()
    exists_c_file_form = ExistsCFileForm()
    editor_c_form = EditorCForm()
    if request.method == 'POST':
        #TODO ADDING TEST IN TO REMOVE
        if main_form.test.data:
            DATA['work_dir'] = request.form.get('work_dir')
            DATA['slum_params'] = request.form.get('slum_params')
            DATA['p4a_flags'] = request.form.get('p4a')
            DATA['autopar_flags'] = request.form.get('autopar')
            DATA['cetus_flags'] = request.form.get('cetus')
            if is_equal_to_yes(request.form.get('save')):
                DATA['save_folder'] = True
            else:
                DATA['save_folder'] = False


            final_code_path = "test.py"
            open_source_file(final_code_path)

            results()
            return render_template('example.html', main_form=main_form, comp_form=comp_form,
                                    source_file=DATA['source_file'],
                                    result_lines=DATA['result_lines'],
                                    output=output_log,
                                    result_file=DATA['result_file'])
        #TODO END REMOVE


        if main_form.submit1.data:
            DATA['work_dir'] = request.form.get('work_dir')
            DATA['slum_params'] = request.form.get('slum_params')
            DATA['p4a_flags'] = request.form.get('p4a')
            DATA['autopar_flags'] = request.form.get('autopar')
            DATA['cetus_flags'] = request.form.get('cetus')
            if is_equal_to_yes(request.form.get('save')):
                DATA['save_folder'] = True
            else:
                DATA['save_folder'] = False
            if is_equal_to_yes(request.form.get('make_file_choice')):
                print(True)
                DATA['is_make_file'] = True
                return render_template('example.html', main_form=main_form, comp_form=comp_form, make_form=make_form,
                                       start_form=start_form)
            else:
                print(False)
                DATA['is_make_file'] = False
                return render_template('example.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form)
        elif exists_file_form.submit2.data:
            DATA['binary_comp_name'] = request.form.get('binary_comp_name')
            DATA['binary_comp_version'] = request.form.get('binary_comp_version')
            DATA['binary_comp_flags'] = request.form.get('binary_comp_flags')
            if is_equal_to_yes(request.form.get('exists_file')):
                DATA['exists_c_file'] = True
                return render_template('example.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form,
                                       exists_c_file_form=exists_c_file_form, start_form=start_form)
            else:
                DATA['exists_c_file'] = False
                return render_template('example.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form,
                                       editor_c_form=editor_c_form, start_form=start_form)
        elif start_form.submit3.data:
            if DATA['is_make_file']:
                DATA['input_dir'] = request.form.get('input_dir')
                DATA['ignore'] = request.form.get('ignore')
                DATA['include'] = request.form.get('include')
                DATA['make_commands'] = request.form.get('make_commands')
                DATA['make_op'] = request.form.get('make_op')
                DATA['make_on'] = request.form.get('make_on')
                DATA['main_file'] = request.form.get('main_file')
                DATA['main_file_p'] = request.form.get('main_file_p')
                DATA['main_file_r_p'] = request.form.get('main_file_r_p')
                DATA['nas_file'] = request.form.get('nas_file')
                return "Run..."
            else:
                if DATA['exists_c_file']:
                    DATA['input_dir'] = request.form.get('input_dir')
                    DATA['main_file'] = request.form.get('main_file')
                    DATA['main_file_p'] = request.form.get('main_file_p')
                    DATA['main_file_r_p'] = request.form.get('main_file_r_p')
                    DATA['nas_file'] = request.form.get('nas_file')
                    return "Run..."
                else:
                    return "Run..."
    return render_template('example.html', main_form=main_form, comp_form=comp_form)


@app.route('/stream_progress')
def stream():
    def generate():
        global output_log
        proc = subprocess.Popen(['python3 -u testt.py'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            output_log += str(line) + "\n"
            yield line.rstrip() + b'\n'
        sleep(5)

    return app.response_class(generate(), mimetype='text/plain')


def results():
    global output_log
    # TODO: take from MAY
    is_copy_paste = True

    if is_copy_paste:
        result_file = ""
        result_lines = ""
        num_of_lines = 1
        # TODO - change it to the real file location
        final_code_path = "test.py"
        with open(final_code_path, "r") as f:
            for line in f:
                result_lines += str(num_of_lines) + " "
                num_of_lines = num_of_lines + 1
                result_file += line
        DATA['result_file'] = result_file
        DATA['result_lines'] = result_lines
        DATA['source_file'] = result_file
        #return render_template('example.html', result_file=result_file, output=output_log, result_lines=result_lines)
        return "GGGGG"
    else:
        # TODO: show link to working dir
        result_file = "main/diretcory"
        # TODO: render template of new page
        return "asd"


if __name__ == "__main__":
    app.debug = True
    app.run()


