import os
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_wtf import Form
from wtforms import StringField, SubmitField, FileField, RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)

DATA = {}


class BasicComparForm(Form):
    work_dir = StringField('Write path for working directory: ', validators=[DataRequired()])
    slum_params = StringField('Slum parameters: ', validators=[DataRequired()])
    save = RadioField('Save folders?', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    make_file_choice = RadioField('Do you want make file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    submit1 = SubmitField('Next')


class MakeFileForm(Form):
    input_dir = StringField('Write path for input directory: ', validators=[DataRequired()])
    ignore = StringField('relative folder paths to be ignored: ', validators=[DataRequired()])
    include = StringField('Include dir names for compilation (relative paths): ', validators=[DataRequired()])
    make_commands = StringField('Makefile Commands: ', validators=[DataRequired()])
    make_op = StringField('Makefile output executable folder (relative path): ', validators=[DataRequired()])
    make_on = StringField('Makefile output executable file name: ', validators=[DataRequired()])
    main_file = StringField('Main c file name: ', validators=[DataRequired()])
    main_file_p = StringField('Main c file parameters: ', validators=[DataRequired()])
    main_file_r_p = StringField('Main c file name relative path: ', validators=[DataRequired()])
    nas_file = RadioField('NAS file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')


class BinaryCompilerForm(Form):
    binary_comp_name = StringField('compiler name: ', validators=[DataRequired()])
    binary_comp_version = StringField('Version: ', validators=[DataRequired()])
    binary_comp_flags = StringField('Flags: ', validators=[DataRequired()])


class CompilersForm(Form):
    p4a = StringField('Par4All flags: ', validators=[DataRequired()])
    autopar = StringField('Autopar flags: ', validators=[DataRequired()])
    cetus = StringField('Cetus flags: ', validators=[DataRequired()])


class ExistsCFileForm(Form):
    input_dir = StringField('Write path for input directory: ', validators=[DataRequired()])
    main_file = StringField('Main c file name: ', validators=[DataRequired()])
    main_file_p = StringField('Main c file parameters: ', validators=[DataRequired()])
    nas_file = RadioField('NAS file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    main_file_r_p = StringField('Main c file name relative path: ', validators=[DataRequired()])


class EditorCForm(Form):
    editor = StringField(u'Write C code', widget=TextArea())


class DoYouHaveExistsFileForm(Form):
    exists_file = RadioField('Do you have an exists files?', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    submit2 = SubmitField('Next')


class StartForm(Form):
    submit3 = SubmitField('Start')


def is_equal_to_yes(data):
    return data == 'yes'


@app.route("/", methods=["GET", "POST"])
@app.route("/compar", methods=["GET", "POST"])
def welcome_label():
    main_form = BasicComparForm()
    make_form = MakeFileForm()
    binary_comp_form = BinaryCompilerForm()
    comp_form = CompilersForm()
    exists_file_form = DoYouHaveExistsFileForm()
    start_form = StartForm()
    exists_c_file_form = ExistsCFileForm()
    editor_c_form = EditorCForm()
    if request.method == 'POST':
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
                DATA['is_make_file'] = True
                return render_template('index.html', main_form=main_form, comp_form=comp_form, make_form=make_form,
                                       start_form=start_form)
            else:
                DATA['is_make_file'] = False
                return render_template('index.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form)
        elif exists_file_form.submit2.data:
            DATA['binary_comp_name'] = request.form.get('binary_comp_name')
            DATA['binary_comp_version'] = request.form.get('binary_comp_version')
            DATA['binary_comp_flags'] = request.form.get('binary_comp_flags')
            if is_equal_to_yes(request.form.get('exists_file')):
                DATA['exists_c_file'] = True
                return render_template('index.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form,
                                       exists_c_file_form=exists_c_file_form, start_form=start_form)
            else:
                return render_template('index.html', main_form=main_form, comp_form=comp_form,
                                       binary_comp_form=binary_comp_form, exists_file_form=exists_file_form,
                                       editor_c_form=editor_c_form, start_form=start_form)
        elif start_form.submit3.data:
            pass
    return render_template('index.html', main_form=main_form, comp_form=comp_form)


# @app.route("/make_choice", methods=["GET", "POST"])
# def show_makefile_choice():
#     makefile_choice = request.form['option']
#     return makefile_choice


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

