""" Setup file for neurolab package """

from distutils.core import setup
import sys
import os


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    except IOError:
        return ''

sys.path.insert(0, 'neurolab')
version = __import__('version').__version__


setup(name='neurolab',
        version=version,
        description='Simple and powerfull neural network library for python',
        long_description = read('doc/src/intro.rst'),
        author='Zuev Evgenij',
        author_email='zueves@gmail.com',
        url='http://code.google.com/p/neurolab',
        packages=['neurolab'],
        scripts=[],

        classifiers=(
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Mathematics',
        ),
        license="LGPL-3",
        keywords="neural network, neural networks, neuron, backpropagation, ann, python, matlab"
    )