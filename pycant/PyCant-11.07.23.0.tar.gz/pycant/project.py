"""Higher-level treatments of structural coverage results
"""

from pycant.ctr import SummableObject


class Project(SummableObject):
    """Extensible set of Functions.
    """

    __slots__ = [
        'functions',
        ]


    def __init__(self):
        super(Project, self).__init__()

        # Indexed set of Functions. Two Functions with the same index are
        # likely to be summed
        self.functions = dict()


    def _key(self, function):
        """Hash function on Function to index them
        """
        return function.file + "|" + function.function


    def initialize(self, test_result):
        """Use corresponding TestResult's Functions to initialize Project.

        ValueError may be raised in case of non compatible Functions in the
        TestResult; this can only occur when test_result is not directly
        issued by Import class.
        """
        for function in test_result.functions:
            key = self._key(function)
            if key in self.functions:
                raise ValueError("TestResult contains non compatible Functions")
            self.functions[key] = function


    def is_summable_function(self, function):
        """True iff the function can integrate the current Project
        """
        key = self._key(function)
        if key not in self.functions:
            return True
        else:
            return self.functions[key].is_summable(function)


    def is_summable(self, other):
        for function in other.functions:
            if not self.is_summable_function(function):
                return False
        return True


    def sum(self, other):
        for function in other.functions:
            key = self._key(function)
            if key in self.functions:
                self.functions[key].sum(function)
            else:
                self.functions[key] = function
