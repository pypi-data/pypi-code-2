"""
Flask-oDesk
-----------
Adds oDesk API support to Flask.

flask-odesk version 0.4.1
(C) 2011 oDesk
"""
__import__('pkg_resources').declare_namespace(__name__)

VERSION = (0, 4, 1, 'beta', 6)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = "%s %s" % (version, VERSION[3])
            if VERSION[4] != 0:
                version = '%s %s' % (version, VERSION[4])
    return version
