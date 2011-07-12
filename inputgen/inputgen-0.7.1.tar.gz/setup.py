from distutils.core import setup
import sys

# Need orderddict and/or multiprocessing to support older Python versions.
dependencies = []
if sys.version_info < (2, 7):
    dependencies.append('ordereddict')
if sys.version_info < (2, 6):
    dependencies.append('multiprocessing')
kwargs = {}
if dependencies:
    kwargs['install_requires'] = dependencies

setup(
    name='inputgen',
    version='0.7.1',
    author='Gary Wilson Jr.',
    author_email='gary.wilson@gmail.com',
    packages=['inputgen', 'inputgen.examples'],
    url='https://bitbucket.org/gdub/python-inputgen',
    license='MIT',
    description=("Tool for automated input generation, useful for bounded"
                 " exhaustive testing and the generation of complex data"
                 " structures for test inputs."),
    long_description=open('README.rst').read(),
    **kwargs
)
