#!/usr/bin/env python

import sys
from hob import __version__, __author__, __author_email__, __program__, __doc__

try:
    from setuptools import setup, find_packages
    addl_args = dict(
        packages=find_packages(),
        entry_points={
        'console_scripts': [
            'hob = hob.script:run_exit',
            ],
        },
        test_suite='nose.collector',
        install_requires=['argparse>=1.0', 'mako'],
        )
except ImportError:
    print >> sys.stderr, "setup.py requires setuptools, install either pip or easy_install"
    sys.exit(1)

## Uncomment the following to generate the data_files list
#from os.path import join, splitext
#from os import walk
#data_files = [
#    (root, [(join(root, f)) for f in files
#      if splitext(f)[1] in ('.mako', '.js', '.css')])
#    for root, d, files in walk('templates')
#   ],
#from pprint import pprint
#pprint(data_files)

setup(
    name=__program__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url='http://bitbucket.org/scope/hob/',
    description=__doc__.splitlines()[0],
    long_description=open('README').read(),
    platforms=['any'],
    data_files=[
        ('templates/html-doc',
          ['templates/html-doc/coredoc.css',
           'templates/html-doc/html-doc-footer.mako',
           'templates/html-doc/html-doc-header.mako',
           'templates/html-doc/html-doc-index.mako',
           'templates/html-doc/html-doc-message.mako',
           'templates/html-doc/html-doc-service.mako',
           'templates/html-doc/html-doc-status.mako']),
         ('templates/js',
          ['templates/js/clientlib_async.js',
           'templates/js/js-build_application.mako',
           'templates/js/js-client-html.mako',
           'templates/js/js-client.mako',
           'templates/js/js-DOM.mako',
           'templates/js/js-field-consts.mako',
           'templates/js/js-helper-const-ids.mako',
           'templates/js/js-http-interface.mako',
           'templates/js/js-message-definition.mako',
           'templates/js/js-runtimes.mako',
           'templates/js/js-service-base.mako',
           'templates/js/js-service-implementation.mako',
           'templates/js/js-message-classes.mako',
           'templates/js/js-stp-0-wrapper.mako',
           'templates/js/js-windows.mako',
           'templates/js/json.js',
           'templates/js/logger.js',
           'templates/js/messagemixin.js',
           'templates/js/messagebroker.js',
           'templates/js/namespace.js',
           'templates/js/simpleconsolelogger.js',
           'templates/js/style.css',
           'templates/js/tag_manager.js',
           'templates/js/test_framework.js',
           'templates/js/message_maps.js',
           'templates/js/get_message_maps.js',
           'templates/js/utils.js']),
         ('templates/proto',
          ['templates/proto/block_options.mako',
           'templates/proto/enum.mako',
           'templates/proto/inline_options.mako',
           'templates/proto/message.mako',
           'templates/proto/package.mako',
           'templates/proto/service.mako']),
         ('templates/rst-doc',
          ['templates/rst-doc/package.mako',
           'templates/rst-doc/rst-doc-service.mako',
           'templates/rst-doc/rst-proto-defs.mako']),
         ('templates',
          ['templates/proto/google/protobuf/descriptor.proto',
           'templates/proto/scope_descriptor.proto']),
      ],
    license='New BSD License',
    keywords='scope protobuf',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Topic :: Software Development :: Code Generators',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development',
      ],
    **addl_args)
