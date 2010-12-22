#! /usr/bin/env python

import sys
import re
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

def main(file):
    lines = open(file).readlines()
    counter = 0
    for line in lines:
        counter += 1
    print str(counter) + " " + re.sub("./", "", file)
    
if __name__ == "__main__":
    file = sys.argv[1]
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main(file)