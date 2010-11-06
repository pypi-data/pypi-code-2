import demain
__main__ = demain.fix()

import bigpackage.bar
import sys

class Foo():
    pass

if __main__:
    sys.exit(0 if (bigpackage.bar.bigpackage.foo.Foo is Foo) else 1)
