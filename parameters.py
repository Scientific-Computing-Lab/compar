
class Parameters:

    def __init__(self, code_params=None, omp_rtl_params=None, compilation_params=None):
        if not code_params:
            code_params = []  # TODO: change name
        if not omp_rtl_params:
            omp_rtl_params = []
        if not compilation_params:
            compilation_params = []
        self.code_params = code_params
        self.omp_rtl_params = omp_rtl_params
        self.compilation_params = compilation_params

    def get_code_params(self):  # TODO: change name
        return self.code_params

    def get_omp_rtl_params(self):
        return self.omp_rtl_params

    def get_compilation_params(self):
        return self.compilation_params

    def set_code_params(self, code_params):  # TODO: change name
        self.code_params = code_params

    def set_omp_rtl_params(self, omp_rtl_params):
        self.omp_rtl_params = omp_rtl_params

    def set_compilation_params(self, compilation_params):
        self.compilation_params = compilation_params

    def add_code_param(self, code_param):  # TODO: change name
        for i, param in enumerate(self.code_params):
            if param.split()[0] == code_param.split()[0]:
                self.code_params[i] = code_param
                return
        self.code_params.append(code_param)

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


