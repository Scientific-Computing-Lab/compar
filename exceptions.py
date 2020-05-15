import os
import json
from combination_validator import CombinationValidator
import jsonschema
from globals import ExceptionConfig, GlobalsConfig, ComparConfig, CombinatorConfig


class FileError(Exception):
    pass


class CompilationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class UserInputError(Exception):
    pass


class FolderError(Exception):
    pass


class DatabaseError(Exception):
    pass


class CombinationFailure(Exception):
    pass


class MissingDataError(Exception):
    pass


class MakefileError(Exception):
    pass


class FragmentError(Exception):
    pass


class DeadCodeLoop(Exception):
    pass


class NoOptimalCombinationError(Exception):
    pass


class DeadCodeFile(Exception):
    pass


def assert_file_exist(file_path: str):
    if not os.path.exists(file_path):
        raise FileError(f'File {file_path} dose not exist')


def assert_file_from_format(file_path: str, _format: str):
    if not os.path.basename(file_path).split('.')[1].endswith(_format):
        raise FileError(f'File {file_path} should be in {_format} format')


def assert_file_is_empty(file: str):
    if not file:
        raise FileError(f'File {file} is empty')


def assert_only_files(folder_path: str):
    folder_content = os.listdir(folder_path)
    if len(folder_content) != len(list(filter(os.path.isfile,
                                              [os.path.join(folder_path, file) for file in folder_content]))):
        raise UserInputError('Input dir must contain only files!')


def assert_rel_path_starts_without_sep(path: str):
    if path.startswith(os.sep):
        raise UserInputError('Relative path should not start with separator!')


def assert_forbidden_characters(path: str):
    forbidden_characters = ["{", "}"]
    for char in forbidden_characters:
        if char in path:
            raise UserInputError(f'Path cannot contain any char from: {forbidden_characters}')


def assert_test_file_name(test_file_name: str):
    if test_file_name != CombinationValidator.UNIT_TEST_FILE_NAME:
        raise UserInputError(f'Unit test file must be named as: {CombinationValidator.UNIT_TEST_FILE_NAME}!')


def assert_test_file_function_name(test_file_path: str):
    if not CombinationValidator.check_if_test_exists(test_file_path):
        raise UserInputError(f'Unit test file must contain test named: "{CombinationValidator.UNIT_TEST_NAME}"!')


def assert_original_files_folder_exists(working_directory: str):
    original_files_path = os.path.join(working_directory, ComparConfig.ORIGINAL_FILES_FOLDER_NAME)
    if not os.path.exists(original_files_path):
        raise UserInputError(f'Original files folder from the last Compar operation must be exist in'
                             f' {working_directory}')


def assert_folder_exist(folder_path: str):
    if not os.path.exists(folder_path):
        raise FolderError(f'Folder {folder_path} dose not exist')


def assert_allowed_directive_type(directive_type: str):
    allowed_types = (CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX, CombinatorConfig.FOR_DIRECTIVE_PREFIX)
    if directive_type not in allowed_types:
        raise UserInputError(f'omp directives prefix of {directive_type} is incorrect!')


def assert_user_json_structure():
    schema_file_path = os.path.join(GlobalsConfig.ASSETS_DIR_PATH, ExceptionConfig.PARAMETERS_SCHEMA_FILE_NAME)
    with open(schema_file_path, 'r') as fp:
        json_schema = json.load(fp)
    args_for_validation_func = (
        (json_schema['compilation'], CombinatorConfig.COMPILATION_PARAMS_FILE_PATH),
        (json_schema['omp_rtl'], CombinatorConfig.OMP_RTL_PARAMS_FILE_PATH),
        (json_schema['omp_directives'], CombinatorConfig.OMP_DIRECTIVES_FILE_PATH)
    )
    for args in args_for_validation_func:
        assert_params_json_is_valid(*args)


def assert_params_json_is_valid(json_schema: dict, json_path: str):
    assert_file_exist(json_path)
    with open(json_path, 'r') as fp:
        params_json = json.load(fp)
    try:
        jsonschema.validate(params_json, json_schema)
    except jsonschema.exceptions.ValidationError:
        raise UserInputError(f'{json_path} must conform to scheme!')
