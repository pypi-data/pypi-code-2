"""
Authors:
    Carlos Ble (www.carlosble.com)
    Ruben Bernardez (www.rubenbp.com)
    www.iExpertos.com
License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
Project home: https://bitbucket.org/carlosble/pydoubles
"""

import safeunicode
import re

# PUBLIC API
def str_containing(substr):
    return _SubstrMatcher_(substr)

def str_not_containing(substr):
    return _NotSubstrMatcher_(substr)

def str_length(arg):
    return _LengthMatcher_(arg)

# CORE API
class PyDoublesMatcher(object):
    matcher_name = "pyDoublesMatcher"

    def __str__(self):
        try:
            return self.matcher_name + " '" + safeunicode.get_string(self.defined_arg) + "'"
        except:
            return str(self.__class__)
        
    def matches(self, received_arg):
        return False

class _LengthMatcher_(PyDoublesMatcher):
    matcher_name = "string with length"    

    def __init__(self, length):
        self.defined_arg = length
    
    def matches(self, text):
        return int(self.defined_arg) == len(text)

class _SubstrMatcher_(PyDoublesMatcher):
    matcher_name = "string containing"  
          
    def __init__(self, substring):
        self.defined_arg = self.__prepare_arg(substring)
    
    def __prepare_arg(self, substring):
        return safeunicode.get_string(substring)
        
    def matches(self, arg2):
        try:
            self.arg2 = self.__prepare_arg(arg2)
            return self._comparison()
        except TypeError:
            return False

    def _comparison(self):
        return re.search(self.defined_arg, self.arg2)

class _NotSubstrMatcher_(_SubstrMatcher_):
    matcher_name = "string NOT containing"     

    def __init__(self, substring):
        super(_NotSubstrMatcher_, self).__init__(substring)

    def _comparison(self):
        return not re.search(self.defined_arg, self.arg2)

class _MatchFinder_():
    def args_dont_match(self, arg1, arg2):
        return not self._args_match(arg1, arg2)

    def _args_match(self, arg1, arg2):
        if self._are_valid_args(arg1, arg2):    
            if self._is_a_matcher_object(arg1):
                return self._matches(arg1, arg2)
            if self._is_a_matcher_object(arg2):
                return self._matches(arg2, arg1)
        return False

    def _are_valid_args(self, arg1, arg2):
        return arg1 is not None and arg2 is not None

    def _is_a_matcher_object(self, arg):
        return callable(self._get_match_method(arg))

    def _get_match_method(self, arg):
        return getattr(arg, "matches", None)
    
    def _matches(self, arg1, arg2):
        match_method = self._get_match_method(arg1)
        return match_method(arg2)