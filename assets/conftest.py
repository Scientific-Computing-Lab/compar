
def pytest_addoption(parser):
    parser.addoption("--working_dir", action="store", default="")
    parser.addoption("--output_file_name", action="store", default="")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    working_dir_option_value = metafunc.config.option.working_dir
    output_file_name_option_value = metafunc.config.option.output_file_name
    if 'working_dir' in metafunc.fixturenames and working_dir_option_value is not None:
        metafunc.parametrize("working_dir", [working_dir_option_value])
    if 'output_file_name' in metafunc.fixturenames and output_file_name_option_value is not None:
        metafunc.parametrize("output_file_name", [output_file_name_option_value])
