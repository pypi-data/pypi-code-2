#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1.11'
DESCRIPTION = 'Python Application/Worker Server'

setup(
    name='PaxDaemonica',
    version=VERSION,
    description=DESCRIPTION,
    author='Jeffrey Jenkins',
    license='MIT',
    zip_safe=False,
    author_email='jeff@qcircles.net',
    url='http://github.com/jeffjenkins/PaxDemonica',
    packages=['paxd', 'paxd.server', 'paxd.monit', 'paxd.app', 'paxd.webuiapp'],
    package_data={
        "" : ["*.js", "*.css", "*.sass"],
    },
    install_requires=['redis', 'smartpool', 'mako'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # 'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)