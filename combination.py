from parameters import Parameters


class Combination:

    @staticmethod
    def json_to_obj(combination_json: dict):
        return Combination(combination_id=combination_json['_id'],
                           compiler_name=combination_json['compiler_name'],
                           parameters=Parameters.json_to_obj(combination_json['parameters']))

    def __init__(self, combination_id: str, compiler_name: str, parameters: Parameters or None):
        self.combination_id = combination_id
        self.compiler_name = compiler_name
        self.parameters = parameters

    def get_combination_id(self):
        return self.combination_id

    def get_compiler(self):
        return self.compiler_name

    def get_parameters(self):
        return self.parameters

    def set_combination_id(self, combination_id: str):
        self.combination_id = combination_id

    def set_compiler(self, compiler_name: str):
        self.compiler_name = compiler_name

    def set_parameters(self, parameters: Parameters or None):
        self.parameters = parameters
