import demain
__main__ = demain.fix()

import bar
import sys

class Foo():
    pass

if __main__:
    sys.exit(0 if (bar.foo.Foo is Foo) else 1)
