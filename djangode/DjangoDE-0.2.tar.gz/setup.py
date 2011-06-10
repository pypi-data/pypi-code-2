#!/usr/bin/env python

from distutils.core import setup

setup(name='DjangoDE',
      version='0.2',
      description='An integrated development environment for Django.',
      author='Andrew Wilkinson',
      author_email='andrewjwilkinson@gmail.com',
      url='http://code.google.com/p/djangode/',
      packages=['djangode', 'djangode.data', 'djangode.gui', 'djangode.project', 'djangode.runner', 'djangode.tests', 'djangode.utils',
                'djangode.data.autocomplete', 'djangode.gui.highlighters', 'djangode.gui.wizards'],
      scripts=['bin/djangode', 'bin/djangode-runner'],
      classifiers=['Development Status :: 3 - Alpha', 'Environment :: X11 Applications :: Qt', 'Framework :: Django',
                   'Intended Audience :: Developers', 'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English', 'Topic :: Text Editors :: Integrated Development Environments (IDE)']
     )
