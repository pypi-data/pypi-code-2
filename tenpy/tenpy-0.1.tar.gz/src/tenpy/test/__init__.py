import os
import sys
from glob import glob
from os.path import (dirname, abspath, splitext)
from test import support


def main():
    for f in os.listdir(dirname(__file__)):
        if f.startswith("test_") and f.endswith(".py"):
            modname = "tenpy.test." + splitext(f)[0]
            __import__(modname)
            support.run_unittest(modname)

if __name__ == "__main__":
    sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
    main()
