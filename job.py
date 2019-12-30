
class Job:
    """
    directory - is the path to the directory the contains tha files of the job
    args - The arguments how send to the job
    combination - list of the combination that make the the job
    sections_runtime - a dictionary that contains all loops in the source file and the time that took him
    """
    def __init__(self, directory, args="", combination=None, sections_runtime={}):
        self.directory = directory
        self.combination = combination
        self.sections_runtime = sections_runtime
        self.args = args

    def get_dir(self):
        return self.directory

    def get_args(self):
        return self.args

    def get_sections_runtime(self):
        return self.sections_runtime

    def get_loop_time_by_label(self, label):
        return self.sections_runtime[label]

    def set_sections_runtime(self, label, time):
        self.sections_runtime[label] = time