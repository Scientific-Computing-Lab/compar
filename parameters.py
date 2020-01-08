
class Parameters:

    def __init__(self, code_params=[], env_params=[], compilation_params=[]):
        self.code_params = code_params
        self.env_params = env_params
        self.compilation_params = compilation_params

    def get_code_params(self):
        return self.code_params

    def get_env_params(self):
        return self.env_params

    def get_compilation_params(self):
        return self.compilation_params

    def set_code_params(self, code_params):
        self.code_params = code_params

    def set_env_params(self, env_params):
        self.env_params = env_params

    def set_compilation_params(self, compilation_params):
        self.compilation_params = compilation_params

    def add_code_param(self, code_param):
        for i, param in enumerate(self.code_params):
            if param.split()[0] == code_param.split()[0]:
                self.code_params[i] = code_param
                return
        self.code_params.append(code_param)

    def add_env_param(self, env_param):
        for i, param in enumerate(self.env_params):
            if param.split()[0] == env_param.split()[0]:
                self.env_params[i] = env_param
                return
        self.env_params.append(env_param)

    def add_compilation_param(self, compilation_param):
        for i, param in enumerate(self.compilation_params):
            if param.split()[0] == compilation_param.split()[0]:
                self.compilation_params[i] = compilation_param
                return
        self.compilation_params.append(compilation_param)


