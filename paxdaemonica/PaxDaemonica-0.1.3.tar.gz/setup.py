#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1.3'
DESCRIPTION = 'Python Application/Worker Server'

setup(
    name='PaxDaemonica',
    version=VERSION,
    description=DESCRIPTION,
    author='Jeffrey Jenkins',
    license='MIT',
    author_email='jeff@qcircles.net',
    url='http://github.com/jeffjenkins/PaxDemonica',
    packages=['paxd', 'paxd.server', 'paxd.monit', 'paxd.app', 'paxd.webuiapp'],
    install_requires=['redis'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # 'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)