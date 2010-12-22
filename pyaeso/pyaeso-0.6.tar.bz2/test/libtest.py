from optparse import OptionParser
import unittest

def main(argv, local_cases, remote_cases):
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--verbosity", type="int", dest="verbosity", default = 1)
    parser.add_option("--with-remote", action="store_true", dest="remote", default=False)

    (opts, args) = parser.parse_args()
    #~ if len(args) != 1:
        #~ parser.error("incorrect number of arguments")

    if opts.remote:
        tests = local_cases + remote_cases
    else:
        tests = local_cases

    suite = unittest.TestSuite(tests)
    result = unittest.TextTestRunner(verbosity=opts.verbosity).run(suite)

    if result.wasSuccessful():
        rc = 0
    else:
        rc = 1

    return rc
