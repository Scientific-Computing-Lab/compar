class Combination:

    COMPAR_COMBINATION_ID = 'compar_combination'

    def __init__(self, combination_id, compiler_name, parameters):
        self.combination_id = combination_id
        self.compiler_name = compiler_name
        self.parameters = parameters

    def get_combination_id(self):
        return self.combination_id

    def get_compiler(self):
        return self.compiler_name

    def get_parameters(self):
        return self.parameters

    def set_combination_id(self, combination_id):
        self.combination_id = combination_id

    def set_compiler(self, compiler_name):
        self.compiler_name = compiler_name

    def set_parameters(self, parameters):
        self.parameters = parameters
