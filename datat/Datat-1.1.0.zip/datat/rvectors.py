"""Utility to make R vectors according to type (e.g. a list of integers will be
converted to an IntVector). Python's None is translated to NA in R. Handles
strings, integers, floats and booleans (True/False).

Usage example:
rvectors.make_r_vector([1,2,3,7,None])   # --> IntVector, last item NA
"""
from rpy2 import robjects

def make_r_vector(things):
    """Return the type of R vector appropriate to the data entered. If data is
    mismatched, try to make a StrVector, and failing that, raise a TypeError.
    
    If passed a dictionary, will try to turn it into a named vector."""
    names = None
    if hasattr(things, "items"):   # dict-like: will add names to vector
        names, things = zip(*things.items())
    
    if all(isinstance(a, str) or a is None for a in things):
        things = [a if not(a is None) else robjects.NA_Character \
                            for a in things]
        vector = robjects.StrVector(list(things))
    elif all(isinstance(a, bool) or a is None for a in things):
        things = [a if not(a is None) else robjects.NA_Logical for a in things]
        vector = robjects.BoolVector(list(things))
    elif all(isinstance(a, int) or a is None for a in things):
        vector = robjects.IntVector(things)
    elif all(isinstance(a, (float, int)) or a is None for a in things):
        vector = robjects.FloatVector(things)
    else:
        try:
            things = [a if not(a is None) else robjects.NA_character \
                                        for a in things]
            vector = robjects.StrVector(things)
        except:
            raise TypeError("Couldn't convert to R vector.")
        
    if names:    # Add names to vector
        vector.names = list(names)
    return vector
