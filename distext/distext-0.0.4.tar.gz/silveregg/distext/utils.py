# XXX: THIS MODULE SHOULD NOT DEPEND ON MONKEYPATCHING ! XXX
import os
import sys
import re

from os.path import \
    join, split, splitext, dirname

_IDPATTERN = "[a-zA-Z_][a-zA-Z_0-9]*"
_DELIM = "$"

def _simple_subst_vars(s, local_vars):
    """Like subst_vars, but does not handle escaping."""
    def _subst(m):
        var_name = m.group(1)
        if var_name in local_vars:
            return local_vars[var_name]
        else:
            raise ValueError("%s not defined" % var_name)
        
    def _resolve(d):
        ret = {}
        for k, v in d.items():
            ret[k] = re.sub("\%s(%s)" % (_DELIM, _IDPATTERN), _subst, v)
        return ret

    ret = _resolve(s)
    while not ret == s:
        s = ret
        ret = _resolve(s)
    return ret

def subst_vars (s, local_vars):
    """Perform shell/Perl-style variable substitution.

    Every occurrence of '$' followed by a name is considered a variable, and
    variable is substituted by the value found in the `local_vars' dictionary.
    Raise ValueError for any variables not found in `local_vars'.

    '$' may be escaped by using '$$'

    Parameters
    ----------
    s: str
        variable to substitute
    local_vars: dict
        dict of variables
    """
    # Resolve variable substitution within the local_vars dict
    local_vars = _simple_subst_vars(local_vars, local_vars)

    def _subst (match):
        named = match.group("named")
        if named is not None:
            if named in local_vars:
                return str(local_vars[named])
            else:
                raise ValueError("Invalid variable '%s'" % named)
        if match.group("escaped") is not None:
            return _DELIM
        raise ValueError("This should not happen")

    def _do_subst(v):
        pattern_s = r"""
        %(delim)s(?:
            (?P<escaped>%(delim)s) |
            (?P<named>%(id)s)
        )""" % {"delim": r"\%s" % _DELIM, "id": _IDPATTERN}
        pattern = re.compile(pattern_s, re.VERBOSE)
        return pattern.sub(_subst, v)

    try:
        return _do_subst(s)
    except KeyError, var:
        raise ValueError("invalid variable '$%s'" % var)

__MONKEY_PATCH = None
def monkey_patch_mode():
    global __MONKEY_PATCH

    if __MONKEY_PATCH is not None:
        return __MONKEY_PATCH
    else:
        if "setuptools" in sys.modules:
            __MONKEY_PATCH = "setuptools"
        else:
            __MONKEY_PATCH = "distutils"
        return __MONKEY_PATCH

def ensure_directory(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)
