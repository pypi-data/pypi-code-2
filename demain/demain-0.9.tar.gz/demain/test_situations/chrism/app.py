# Adapted from Chris McDonough's example at:
# http://docs.pylonshq.com/pyramid/dev/designdefense.html#application-programmers-don-t-control-the-module-scope-codepath-import-time-side-effects-are-evil

import demain
__main__ = demain.fix()

from config import decorator
from config import L
import sys

@decorator
def foo():
    pass

if __main__:
    import app2
    sys.exit(0 if (len(L) == 2) else 1)
