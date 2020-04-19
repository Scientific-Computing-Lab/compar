
class Parameters:

    @staticmethod
    def json_to_obj(parameters_json):
        return Parameters(omp_directives_params=parameters_json['omp_directives_params'],
                          omp_rtl_params=parameters_json['omp_rtl_params'],
                          compilation_params=parameters_json['compilation_params'])

    def __init__(self, omp_directives_params=None, omp_rtl_params=None, compilation_params=None):
        if not omp_directives_params:
            omp_directives_params = []
        if not omp_rtl_params:
            omp_rtl_params = []
        if not compilation_params:
            compilation_params = []
        self.omp_directives_params = omp_directives_params
        self.omp_rtl_params = omp_rtl_params
        self.compilation_params = compilation_params

    def get_omp_directives_params(self):
        return self.omp_directives_params

    def get_omp_rtl_params(self):
        return self.omp_rtl_params

    def get_compilation_params(self):
        return self.compilation_params

    def set_omp_directives_params(self, omp_directives_params):
        self.omp_directives_params = omp_directives_params

    def set_omp_rtl_params(self, omp_rtl_params):
        self.omp_rtl_params = omp_rtl_params

    def set_compilation_params(self, compilation_params):
        self.compilation_params = compilation_params

    def add_omp_directives_param(self, omp_directives_param):
        for i, param in enumerate(self.omp_directives_params):
            if param.split()[0] == omp_directives_param.split()[0]:
                self.omp_directives_params[i] = omp_directives_param
                return
        self.omp_directives_params.append(omp_directives_param)

    def add_omp_rtl_param(self, omp_rtl_param):
        for i, param in enumerate(self.omp_rtl_params):
            if param.split()[0] == omp_rtl_param.split()[0]:
                self.omp_rtl_params[i] = omp_rtl_param
                return
        self.omp_rtl_params.append(omp_rtl_param)

    def add_compilation_param(self, compilation_param):
        for i, param in enumerate(self.compilation_params):
            if param.split()[0] == compilation_param.split()[0]:
                self.compilation_params[i] = compilation_param
                return
        self.compilation_params.append(compilation_param)


