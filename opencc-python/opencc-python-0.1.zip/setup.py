from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

extra = {}

try:
    from opencc import version
    version = version.__version__
except ImportError:
    version = 'unknown'

try:
    file = open('README.rst', 'rt')
    content = file.read()
    file.close()
    extra['long_description'] = content
except IOError:
    pass

setup(
    name='opencc-python',
    version=version,
    description='A Python wrapper for Open Chinese Convert',
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    url='http://bitbucket.org/victorlin/opencc_python',
    license='MIT',
    packages=find_packages(),
    package_data={
        'opencc': [
            'bin/*',
            'data/*'
        ]
    },
    install_requires=['distribute'],
    **extra
)