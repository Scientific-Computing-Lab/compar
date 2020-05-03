import itertools
import json
from globals import CombinatorConfig


def generate_combinations():
    omp_rtl_params = []
    combinations = []
    with open(CombinatorConfig.OMP_RTL_PARAMS_FILE_PATH, 'r') as fp:
        omp_rtl_array = json.load(fp)
    for param in omp_rtl_array:
        omp_rtl_params.append(generate_omp_rtl_params(param))
    omp_rtl_params = mult_lists(omp_rtl_params)

    omp_directives_params = generate_omp_directive_params()

    with open(CombinatorConfig.COMPILATION_PARAMS_FILE_PATH, 'r') as fp:
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
                for omp_directives_comb in omp_directives_params:
                    if not omp_rtl_comb:
                        curr_omp_rtl_comb = []
                    else:
                        curr_omp_rtl_comb = omp_rtl_comb.split(f"{CombinatorConfig.PARAMS_SEPARATOR}")
                    if not compile_comb:
                        curr_compile_comb = []
                    else:
                        curr_compile_comb = compile_comb.split(f"{CombinatorConfig.PARAMS_SEPARATOR}")
                    if not omp_directives_comb:
                        curr_omp_directives_comb = []
                    else:
                        curr_omp_directives_comb = omp_directives_comb.split(f"{CombinatorConfig.PARAMS_SEPARATOR}")
                    new_comb = {
                        "compiler_name": compiler,
                        "parameters": {
                            "omp_rtl_params": curr_omp_rtl_comb,
                            "omp_directives_params": curr_omp_directives_comb,
                            "compilation_params": curr_compile_comb
                        }
                    }
                    combinations.append(new_comb)
    return combinations


def generate_omp_directive_params():
    with open(CombinatorConfig.OMP_DIRECTIVES_FILE_PATH, 'r') as fp:
        json_omp_directives = json.load(fp)
    parallel_directive_params = json_omp_directives['parallel']
    for_directive_params = json_omp_directives['for']
    omp_directives_params = []
    omp_directives_params.extend(generate_directive_list_from_json(parallel_directive_params,
                                                                   CombinatorConfig.PARALLEL_DIRECTIVE_PREFIX))
    omp_directives_params.extend(generate_directive_list_from_json(for_directive_params,
                                                                   CombinatorConfig.FOR_DIRECTIVE_PREFIX))
    return mult_lists(omp_directives_params)


def generate_directive_list_from_json(params: dict, pragma_type: str):
    valued_params = generate_valued_directive_params(params['valued'], pragma_type)
    toggle_params = generate_toggle_directive_params(params['toggle'], pragma_type)
    return valued_params + toggle_params


def generate_valued_directive_params(valued_params_list: list, pragma_type: str):
    params_list = []
    for param in valued_params_list:
        current_params = []
        pragma_name = param['pragma']
        for value in param['values']:
            val = value['val']
            if value['related']:
                for rel_val in value['related']:
                    current_params.append(f'{pragma_type}_{pragma_name}({val}, {rel_val})')
            else:
                current_params.append(f'{pragma_type}_{pragma_name}({val})')
        params_list.append(current_params)
    return params_list


def generate_toggle_directive_params(toggle_params_list: list, pragma_type: str):
    return [[f'{pragma_type}_{param}', ] for param in toggle_params_list]


def generate_toggle_params_list(toggle: list, mandatory: bool = False):
    lst = []
    for val in toggle:
        lst.append(generate_toggle_params(val, mandatory))
    return lst


def generate_toggle_params(toggle: str, mandatory: bool = False):
    if not toggle:
        return [""]

    lst = []
    if not mandatory:
        lst.append("")
    lst.append(toggle)
    return lst


def generate_valued_params(valued: dict, mandatory: bool = False):
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


def generate_valued_params_list(valued_list: list, mandatory: bool = False):
    lst = []
    for valued in valued_list:
        lst.append(generate_valued_params(valued, mandatory))
    return lst


def generate_omp_rtl_params(param: dict):
    if not param:
        return [""]
    lst = []
    param_name = param["param"]
    for val in param["vals"]:
        lst.append(f"{param_name}({val});")
    return lst


def mult_lists(lst: list):
    mult_list = []
    for i in itertools.product(*lst):
        i = list(filter(None, i))  # filter empty elements
        mult_list.append(f"{CombinatorConfig.PARAMS_SEPARATOR}".join(i))
    return mult_list
