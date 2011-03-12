#! /usr/bin/env python
#
# results_attributes
#

import sys

def main():
    if len(sys.argv) > 1:
        print "results_attributes  - Print the predefined attributes in a SolverResults object"

    from pyutilib.misc import Options
    from coopr.opt import SolverResults
    options = Options(schema=True)
    r=SolverResults()
    repn = r._repn_(options)
    r.pprint(sys.stdout, options, repn=repn)
