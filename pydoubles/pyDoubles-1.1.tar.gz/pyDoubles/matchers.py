import safeunicode
import re

PYDOUBLES_MATCHER = "__PYDOUBLES_MATCHER_"

PYDOUBLES_CONTAINING = "__CONTAINING_"
PYDOUBLES_NOT_CONTAINING = "__NOT_containing_"
PYDOUBLES_LENGTH = "__LENGHT_"

# PUBLIC API
def str_containing(substr):
    return PYDOUBLES_MATCHER + PYDOUBLES_CONTAINING + substr 

def str_not_containing(substr):
    return PYDOUBLES_MATCHER + PYDOUBLES_NOT_CONTAINING + substr

def str_length(arg):
    return PYDOUBLES_MATCHER + PYDOUBLES_LENGTH + str(arg)

# CORE API

class _SubstrMatcher_(object):
    name = PYDOUBLES_CONTAINING
    
    def _prepare_args(self, arg1, arg2):
        self.arg1 = safeunicode.get_string(arg1)
        self.arg2 = safeunicode.get_string(arg2)
        
    def comparison(self):
        return re.search(self.arg1, self.arg2)
    
    def is_matcher(self):
        try:
            return re.search(PYDOUBLES_MATCHER, self.arg1) and \
                   re.search(self.name, self.arg1)
        except TypeError:
            return False
               
    def clean_args(self):
        self.arg1 = self.arg1.replace(PYDOUBLES_MATCHER, "")
        self.arg1 = self.arg1.replace(self.name, "")
        
    def does_it_apply(self, arg1, arg2):
        self._prepare_args(arg1, arg2)
        if self.is_matcher():
           self.clean_args()
           return self.comparison()
        return False


class _NotSubstrMatcher_(_SubstrMatcher_):
    name = PYDOUBLES_NOT_CONTAINING
    
    def comparison(self):
        return not re.search(self.arg1, self.arg2)


class _LengthMatcher_(_SubstrMatcher_):
    name = PYDOUBLES_LENGTH
    
    def comparison(self):
        return int(self.arg1) == len(self.arg2) 
    
        
class _Matchers_():
    def no_one_applies(self, arg1, arg2):
        matchers = [_SubstrMatcher_(), _NotSubstrMatcher_(),
                    _LengthMatcher_()]
        for matcher in matchers:       
            if matcher.does_it_apply(arg1, arg2) or \
               matcher.does_it_apply(arg2, arg1):
                return False
        return True
    
 