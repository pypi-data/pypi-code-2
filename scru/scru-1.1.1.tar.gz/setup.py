#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='Scru',
    version='1.0.0',
    description='Screenshot Uploader.',
    author='Roberto Gea (Alquimista)',
    author_email='alquimistaotaku@gmail.com',
    license='MIT',
    packages=['scru'],
    install_requires=['python-notify', 'plac'],
    data_files=[
        ('/usr/bin', ['bin/scru']),
        ('/usr/bin', ['bin/scru-openbox-pipemenu']),
        ('/usr/share/sounds', ['sounds/scru_shot.wav']),
        ('/usr/share/icons/hicolor/scalable/apps', ['icons/scru.svg']),
        ('/usr/share/licenses/scru', ['LICENSE'])],
    )
