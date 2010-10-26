#!/usr/bin/env python

#You need to have i18ndude in your system path to run it

import subprocess, sys, os

from config import PROJECTNAME

DOMAIN = PRODUCT = PROJECTNAME

def generate():
    command = "i18ndude rebuild-pot --pot i18n/generated.pot --create %s ." % (DOMAIN,)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

def merge():
    print "Merging manual entries"
    command = "i18ndude merge --pot i18n/generated.pot --merge i18n/manual.pot"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

def sync():
    print "Syncing i18n files"
    command = "i18ndude sync --pot i18n/generated.pot i18n/%s*.po" % (DOMAIN,)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

generate()
merge()
sync()
print 'All done'