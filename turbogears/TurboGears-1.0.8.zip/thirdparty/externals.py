#!/usr/bin/env python
"""Check out/update working copies of third-party dependency repositories."""

import os
import sys
import popen2
import re

externals = {
    "cherrypy": "http://svn.cherrypy.org/tags/cherrypy-2.3.0/",
    "configobj": "http://svn.pythonutils.python-hosting.com/tags/configobj-4.3.2/",
    "decoratortools": "svn://svn.eby-sarna.com/svnroot/DecoratorTools/",
    "elixir": "http://elixir.ematia.de/svn/elixir/tags/0.6.0/",
    "formencode": "http://svn.formencode.org/FormEncode/tags/1.0.1/",
    "genshi": "http://svn.edgewall.org/repos/genshi/tags/0.5.1/",
    # Kid's SVN server gives "connection refused"
    #"kid": "svn://svn.kid-templating.org/tags/0.9.6/",
    "mochikit": "http://svn.mochikit.com/mochikit/tags/MochiKit-1.3.1/",
    "nose": "http://python-nose.googlecode.com/svn/tags/0.10.2-release/",
    "paste": "http://svn.pythonpaste.org/Paste/tags/1.7.1/",
    "pastescript": "http://svn.pythonpaste.org/Paste/Script/tags/1.6.3/",
    "simplejson": "http://simplejson.googlecode.com/svn/tags/simplejson-1.9.2/",
    "sqlalchemy": "http://svn.sqlalchemy.org/sqlalchemy/tags/rel_0_4_7/",
    "sqlobject": "http://svn.colorstudy.com/SQLObject/branches/0.10/",
}

urlline = re.compile("^URL: (.*)")

def update(proj):
    # We do not use the "subprocess" module for Python 2.3 compability
    os.chdir(proj)
    cout, cin = popen2.popen2('svn info')
    cin.close()
    line = cout.readline()
    while line:
        line = cout.readline().strip()
        url = urlline.match(line)
        if url:
            url = url.group(1).strip()
            if url != externals[proj] and url != externals[proj][:-1]:
                print "Switching project %s to %s" % (proj, externals[proj])
                os.system('svn switch "%s" .' % externals[proj])
            else:
                print "Updating project %s." % (proj)
                print "Repository-URL: %s" % externals[proj]
                os.system('svn update')
            break
    cout.close()
    if not url:
        print "Error! Unable to find URL for project %s."
    os.chdir(os.pardir)

def checkout(proj):
    print "Checking out %s from %s." % (proj, externals[proj])
    os.system('svn checkout "%s" "%s"' % (externals[proj], proj))

def run():
    if not os.path.exists("externals.py"):
        print "You must run this script from the thirdparty directory."
        sys.exit(1)

    for proj in externals:
        if os.path.exists(proj):
            update(proj)
        else:
            checkout(proj)

if __name__ == "__main__":
    run()
