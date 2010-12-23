#!/usr/bin/env python
#
#

import os.path

if os.path.isfile("/etc/debian_version") and os.path.isdir("/var/lib/me2"):
    target = "/var/lib/me2"
else:
    target = "me2"

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print "%s does not exist" % dir ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

setup(
    name='me2',
    version='0.1a1',
    url='http://botme2.googlecode.com/',
    download_url="http://code.google.com/p/botme2/downloads", 
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='The bot for you!',
    license='MIT',
    scripts=['bin/me2',
             'bin/me2-init',
             'bin/me2-irc', 
             'bin/me2-fleet', 
             'bin/me2-xmpp', 
             'bin/me2-release',
             'bin/me2-rollback',
             'bin/me2-run',
             'bin/me2-stop',
             'bin/me2-udp',
             'bin/me2-upload',
             'bin/me2-uploadall'],
    packages=['me2',
              'me2.lib', 
              'me2.utils', 
              'me2.lib.console',
              'me2.lib.gae',
              'me2.lib.gae.utils',
              'me2.lib.gae.web',
              'me2.lib.gae.wave',
              'me2.lib.gae.xmpp',
              'me2.lib.socklib',
              'me2.lib.socklib.irc',
              'me2.lib.socklib.xmpp',
              'me2.lib.socklib.utils',
              'me2.lib.socklib.rest',
              'me2.contrib',
              'me2.contrib.simplejson',
              'me2.contrib.tweepy',
              'me2.plugs',
              'me2.plugs.core',
              'me2.plugs.wave',
              'me2.plugs.common',
              'me2.plugs.socket', 
              'me2.plugs.gae',
              'me2.plugs.myplugs'],
    long_description = """ BOTME2 is a remote event-driven framework for building bots that talk JSON to each other over XMPP. IRC/Console/XMPP (shell) Wave/Web/XMPP (GAE) implementations provided. """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: Other OS',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    data_files=[(target + os.sep + 'data', uploadlist(target + os.sep + 'data')),
                (target + os.sep + 'data' + os.sep + 'examples', uploadfiles('me2' + os.sep + 'data' + os.sep + 'examples')),
                (target + os.sep + 'upload', uploadfiles('me2' + os.sep + 'upload')),
                (target + os.sep + 'upload' + os.sep + 'webapp2', uploadlist('me2' + os.sep + 'upload' + os.sep + 'webapp2')),
                (target + os.sep + 'upload' + os.sep + 'assets', uploadlist('me2' + os.sep + 'upload' + os.sep + 'assets')),
                (target + os.sep + 'upload' + os.sep + 'templates', uploadlist('me2' + os.sep + 'upload' + os.sep +'templates')),
                (target + os.sep + 'upload' + os.sep + 'waveapi', uploadlist('me2' + os.sep + 'upload' + os.sep + 'waveapi')),
                (target + os.sep + 'upload' + os.sep + 'waveapi' + os.sep + 'oauth', uploadlist('me2' + os.sep + 'upload' + os.sep + 'waveapi' + os.sep + 'oauth')),
                (target + os.sep + 'upload' + os.sep + 'waveapi' + os.sep + 'simplejson', uploadlist('me2' + os.sep + 'upload' + os.sep + 'waveapi' + os.sep + 'simplejson')),
                (target + os.sep + 'upload' + os.sep + 'gadgets', uploadlist('me2' + os.sep + 'upload' + os.sep + 'gadgets'))],
)
