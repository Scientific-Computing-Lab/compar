import os
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_wtf import Form
from wtforms import StringField, SubmitField, FileField, RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

DATA = {}


class BasicComparForm(Form):
    work_dir = StringField('Write path for working directory: ', validators=[DataRequired()])
    input_dir = StringField('Write path for input directory: ', validators=[DataRequired()])
    make_file_choice = RadioField('Do you want make file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    submit1 = SubmitField('Next')


class MakeFileForm(Form):
    commands = StringField('Commands: ', validators=[DataRequired()])
    location = StringField('Location: ', validators=[DataRequired()])
    file_name = StringField('File name: ', validators=[DataRequired()])


class BinaryCompilerForm(Form):
    binary_comp_name = StringField('compiler name: ', validators=[DataRequired()])
    binary_comp_version = StringField('Version: ', validators=[DataRequired()])
    binary_comp_flags = StringField('Flags: ', validators=[DataRequired()])


class CompilersForm(Form):
    p4a = StringField('Par4All flags: ', validators=[DataRequired()])
    autopar = StringField('Autopar flags: ', validators=[DataRequired()])
    cetus = StringField('Cetus flags: ', validators=[DataRequired()])


class ExistsCFileForm(Form):
    c_file_name = StringField('File name: ', validators=[DataRequired()])
    c_file_parameters = StringField('Parameters: ')
    nas_file = RadioField('NAS file?', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    c_file_path = FileField('Choose file path: ')


class EditorCForm(Form):
    editor = StringField(u'Write C code', widget=TextArea())


class FlagsForm(Form):
    save = RadioField('Save folders?', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    ignore = StringField('Ignore: ')
    include = StringField('Include: ')


class DoYouHaveExistsFileForm(Form):
    exists_file = RadioField('Do you have an exists file?', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
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
    flags_form = FlagsForm()
    exists_file_form = DoYouHaveExistsFileForm()
    start_form = StartForm()
    exists_c_file_form = ExistsCFileForm()
    editor_c_form = EditorCForm()
    if request.method == 'POST':
        if main_form.submit1.data:
            DATA['work_dir'] = request.form.get('work_dir')
            DATA['input_dir'] = request.form.get('input_dir')
            makefile_choice = request.form.get('make_file_choice')
            if is_equal_to_yes(makefile_choice):
                DATA['make_file'] = True
                return render_template('home.html', form=main_form, make_form=make_form, start_form=start_form)
            else:
                DATA['make_file'] = False
                return render_template('home.html', form=main_form, binary_comp_form=binary_comp_form,
                                       comp_form=comp_form, flags_form=flags_form, exists_file_form=exists_file_form)
        elif exists_file_form.submit2.data:
            DATA['binary_comp_name'] = request.form.get('binary_comp_name')
            DATA['binary_comp_version'] = request.form.get('binary_comp_version')
            DATA['binary_comp_flags'] = request.form.get('binary_comp_flags')
            DATA['p4a_flags'] = request.form.get('p4a')
            DATA['autopar_flags'] = request.form.get('autopar')
            DATA['cetus_flags'] = request.form.get('cetus')
            if is_equal_to_yes(request.form.get('save')):
                DATA['save_folder'] = True
            else:
                DATA['save_folder'] = False
            DATA['ignore'] = request.form.get('ignore')
            DATA['include'] = request.form.get('include')
            exists_file_choice = request.form.get('exists_file')
            if is_equal_to_yes(exists_file_choice):
                DATA['exists_c_file'] = True
                return render_template('home.html', form=main_form, binary_comp_form=binary_comp_form,
                                       comp_form=comp_form, flags_form=flags_form, exists_file_form=exists_file_form,
                                       exists_c_file_form=exists_c_file_form, start_form=start_form)
            else:
                return render_template('home.html', form=main_form, binary_comp_form=binary_comp_form,
                                       comp_form=comp_form, flags_form=flags_form, exists_file_form=exists_file_form,
                                       editor_c_form=editor_c_form, start_form=start_form)
    return render_template('home.html', form=main_form)


# @app.route("/make_choice", methods=["GET", "POST"])
# def show_makefile_choice():
#     makefile_choice = request.form['option']
#     return makefile_choice


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

