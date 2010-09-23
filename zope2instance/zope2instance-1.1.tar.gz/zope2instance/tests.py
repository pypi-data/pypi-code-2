# Copyright (c) 2010 Simplistix Ltd
#
# See license.txt for more details.

from doctest import REPORT_NDIFF,ELLIPSIS, Example
from glob import glob
from manuel import doctest,codeblock,capture
from manuel.testing import TestSuite
from os.path import dirname,join,pardir
from pkg_resources import working_set, Requirement
from socket import socket
from testfixtures import TempDirectory
from testfixtures.manuel import Files
from time import sleep
from zope.testing import renormalizing

import os
import re
import shutil
import zc.buildout.testing

def install_with_deps(test,*packages):
    base = os.path.join(
        test.globs['sample_buildout'],'eggs'
        )

    seen = set()

    for dist in working_set.resolve(
        [Requirement.parse(p) for p in packages]
        ):
        name = dist.project_name
        if name in seen or name=='setuptools':
            continue
        seen.add(name)
        open(os.path.join(base, name+'.egg-link'), 'w'
             ).write(dist.location)

options = REPORT_NDIFF|ELLIPSIS
checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile('#![^\n]+\n'), ''),                
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    # do a develop install of the recipe
    zc.buildout.testing.install_develop('zope2instance', test)
    # recipe eggs
    zc.buildout.testing.install('gocept.recipe.deploymentsandbox', test)
    zc.buildout.testing.install('mailinglogger', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    # install Zope2 along with all its dependencies
    install_with_deps(test,'Zope2')
    # setup the tempdir for testfixtures.manuel
    test.globs['td']=td=TempDirectory(path=os.getcwd())
    # make the root of the tempdir accessible
    test.globs['dir'] = os.path.realpath(
        os.path.join(td.path,os.pardir,os.pardir)
        )
    # a handy function to let us do single replacements
    def replace(path,old,new):
        text = td.read(path)
        if old not in text:
            raise ValueError('%r not found in %r' % (
                old,text
                ))
        td.write(path,text.replace(old,new))
    test.globs['replace']=replace
    # general output checker
    def check(want,got):
        if not checker.check_output(want,got,options):
            raise AssertionError(
                '\n'+checker.output_difference(
                    Example(want,want),got,options
                    ))
    test.globs['check']=check
    # a free port
    s = socket()
    s.bind(('', 0))
    test.globs['port'] = str(s.getsockname()[1])
    # wait for the magic log string
    def wait_for_started(path):
        slept = 0
        while True:
            try:
                if 'Zope Ready to handle requests' in td.read(path):
                    break
            except IOError:
                pass
            if slept>10:
                raise RuntimeError("instance didn't start in time")
            sleep(0.1)
            slept += 0.1
    test.globs['wait_for_started']=wait_for_started
    
def test_suite():
    m =  doctest.Manuel(
        optionflags=options,
        checker=checker,
        )
    m += codeblock.Manuel()
    m += capture.Manuel()
    m += Files('td')
    return TestSuite(
        m,
        join(dirname(__file__),pardir,'docs','use.txt'),
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        )
