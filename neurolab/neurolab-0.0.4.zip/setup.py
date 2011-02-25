""" Setup file for neurolab package """

from distutils.core import setup

def read(fname):
    import os
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    except IOError:
        return ''


setup(name='neurolab',
        version='0.0.4',
        description='Simple and powerfull neural network library for python',
        long_description = read('doc_src/intro.rst'),
        author='Zuev Evgenij',
        author_email='zueves@gmail.com',
        url='http://code.google.com/p/neurolab',
        packages=['src'],
        scripts=[],

        classifiers=(
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ),
        license="LGPL-3",
    )