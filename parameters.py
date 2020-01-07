
class Parameters:

    def __init__(self):
        self.code_params = []
        self.env_params = []
        self.compilation_params = []

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
        if code_param in self.code_params:
            raise Exception("code param: " + str(code_param) + " already exist but has been copied.")
        self.code_params.append(code_param)

    def add_env_param(self, env_param):
        if env_param in self.env_params:
            raise Exception("env param: " + str(env_param) + " already exist but has been copied.")
        self.env_params.append(env_param)

    def add_compilation_param(self, compilation_param):
        if compilation_param in self.compilation_params:
            raise Exception("compilation param: " + str(compilation_param) + " already exist but has been copied.")
        self.compilation_params.append(compilation_param)

    def remove_code_param(self, code_param):
        if code_param in self.code_params:
            self.code_params.remove(code_param)
        else:
            raise Exception("code param: " + str(code_param) + "does not exist.")

    def remove_env_param(self, env_param):
        if env_param in self.env_params:
            self.env_params.remove(env_param)
        else:
            raise Exception("env param: " + str(env_param) + "does not exist.")

    def remove_compilation_param(self, compilation_param):
        if compilation_param in self.compilation_params:
            self.compilation_params.remove(compilation_param)
        else:
            raise Exception("compilation param: " + str(compilation_param) + "does not exist.")
