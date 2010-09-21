#! /usr/bin/env python

import os, subprocess, sys, traceback

def foldlines(s):
    return s.replace("\n", " ").replace("\r", "")

def print_platform():
    print
    try:
        import platform
        out = platform.platform()
        print
        print "platform:", out.replace("\n", " ")
    except EnvironmentError:
        sys.stderr.write("Got exception using 'platform'. Exception follows\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass

def print_python_ver():
    print
    print "python:", foldlines(sys.version)
    print 'maxunicode: ' + str(sys.maxunicode)

def print_stdout(cmdlist, label=None):
    print
    try:
        res = subprocess.Popen(cmdlist, stdin=open(os.devnull),
                               stdout=subprocess.PIPE).communicate()[0]
        if label is None:
            label = cmdlist[0]
        print label + ': ' + foldlines(res)
    except EnvironmentError:
        sys.stderr.write("\nGot exception invoking '%s'. Exception follows.\n" % (cmdlist[0],))
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass

def print_as_ver():
    print
    if os.path.exists('a.out'):
        print "WARNING: a file named a.out exists, and getting the version of the 'as' assembler writes to that filename, so I'm not attempting to get the version of 'as'."
        return
    try:
        res = subprocess.Popen(['as', '-version'], stdin=open(os.devnull),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print 'as: ' + foldlines(res[0]+' '+res[1])
        if os.path.exists('a.out'):
            os.remove('a.out')
    except EnvironmentError:
        sys.stderr.write("\nGot exception invoking '%s'. Exception follows.\n" % ('as',))
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass

def print_setuptools_ver():
    print
    try:
        import pkg_resources
        out = str(pkg_resources.require("setuptools"))
        print "setuptools:", foldlines(out)
    except (ImportError, EnvironmentError):
        sys.stderr.write("\nGot exception using 'pkg_resources' to get the version of setuptools. Exception follows\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass

def print_py_pkg_ver(pkgname):
    print
    try:
        import pkg_resources
        out = str(pkg_resources.require(pkgname))
        print pkgname + ': ' + foldlines(out)
    except (ImportError, EnvironmentError):
        sys.stderr.write("\nGot exception using 'pkg_resources' to get the version of %s. Exception follows.\n" % (pkgname,))
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass
    except pkg_resources.DistributionNotFound:
        sys.stderr.write("\npkg_resources reported no %s package installed. Exception follows.\n" % (pkgname,))
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        pass

print_platform()

print_python_ver()

print_stdout(['buildbot', '--version'])
print_stdout(['cl'])
print_stdout(['g++', '--version'])
print_stdout(['cryptest', 'V'])
print_stdout(['darcs', '--version'])
print_stdout(['darcs', '--exact-version'], label='darcs-exact-version')
print_stdout(['7za'])

print_as_ver()

print_setuptools_ver()

print_py_pkg_ver('coverage')
print_py_pkg_ver('trialcoverage')
print_py_pkg_ver('setuptools_trial')
print_py_pkg_ver('setuptools_darcs')
print_py_pkg_ver('darcsver')
