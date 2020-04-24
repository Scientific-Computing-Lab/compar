import itertools
import json


COMPILATION_PARAMS_FILE_PATH = "assets/compilation_params.json"
OMP_RTL_PARAMS_FILE_PATH = "assets/omp_rtl_params.json"
PARAMS_SEPARATOR = '____compar____params____separator____'


def generate_combinations():
    omp_rtl_params = []
    combinations = []
    with open(OMP_RTL_PARAMS_FILE_PATH, 'r') as fp:
        omp_rtl_array = json.load(fp)
    for param in omp_rtl_array:
        omp_rtl_params.append(generate_omp_rtl_params(param))
    omp_rtl_params = mult_lists(omp_rtl_params)

    with open(COMPILATION_PARAMS_FILE_PATH, 'r') as fp:
        compilation_flags_array = json.load(fp)
    for comb in compilation_flags_array:
        compiler = comb["compiler"]
        essential_valued_params_list = generate_valued_params_list(comb["essential_params"]["valued"], True)
        essential_valued_params_list = mult_lists(essential_valued_params_list)
        essential_toggle_params_list = generate_toggle_params_list(comb["essential_params"]["toggle"], True)
        essential_toggle_params_list = mult_lists(essential_toggle_params_list)

        optional_valued_params_list = generate_valued_params_list(comb["optional_params"]["valued"])
        optional_valued_params_list = mult_lists(optional_valued_params_list)
        optional_toggle_params_list = generate_toggle_params_list(comb["optional_params"]["toggle"])
        optional_toggle_params_list = mult_lists(optional_toggle_params_list)

        all_compilation_params = [essential_valued_params_list, essential_toggle_params_list,
                                  optional_valued_params_list, optional_toggle_params_list]
        all_compilation_params = mult_lists(list(filter(None, all_compilation_params)))  # filter empty lists

        for compile_comb in all_compilation_params:
            for omp_rtl_comb in omp_rtl_params:
                if not omp_rtl_comb:
                    curr_omp_rtl_comb = []
                else:
                    curr_omp_rtl_comb = omp_rtl_comb.split(f"{PARAMS_SEPARATOR}")
                if not compile_comb:
                    curr_compile_comb = []
                else:
                    curr_compile_comb = compile_comb.split(f"{PARAMS_SEPARATOR}")
                new_comb = {
                    "compiler_name": compiler,
                    "parameters": {
                        "omp_rtl_params": curr_omp_rtl_comb,
                        "omp_directives_params": [],
                        "compilation_params": curr_compile_comb
                    }
                }
                combinations.append(new_comb)
    return combinations


def generate_toggle_params_list(toggle, mandatory=False):
    lst = []
    for val in toggle:
        lst.append(generate_toggle_params(val, mandatory))
    return lst


def generate_toggle_params(toggle, mandatory=False):
    if not toggle:
        return [""]

    lst = []
    if not mandatory:
        lst.append("")
    lst.append(toggle)
    return lst


def generate_valued_params(valued, mandatory=False):
    if not valued:
        return [""]

    lst = []
    if not mandatory:
        lst.append("")

    param = valued["param"]
    annotation = valued["annotation"]
    for val in valued["values"]:
        lst.append(f'{param}{annotation}{val}')
    return lst


def generate_valued_params_list(valued_list, mandatory=False):
    lst = []
    for valued in valued_list:
        lst.append(generate_valued_params(valued, mandatory))
    return lst


def generate_omp_rtl_params(param):
    if not param:
        return [""]
    lst = []
    param_name = param["param"]
    for val in param["vals"]:
        lst.append(f"{param_name}({val});")
    return lst


def mult_lists(lst):
    mult_list = []
    for i in itertools.product(*lst):
        i = list(filter(None, list(i)))  # filter empty lists
        mult_list.append(f"{PARAMS_SEPARATOR}".join(i))
    return mult_list
