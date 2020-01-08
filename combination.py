class Combination:

    def __init__(self, combination_id, compiler, parameters):
        self.combination_id = combination_id
        self.compiler = compiler
        self.parameters = parameters

    def get_combination_id(self):
        return self.combination_id

    def get_compiler(self):
        return self.compiler

    def get_parameters(self):
        return self.parameters

    def set_combination_id(self, combination_id):
        self.combination_id = combination_id

    def set_compiler(self, compiler):
        self.compiler = compiler

    def set_parameters(self, parameters):
        self.parameters = parameters
