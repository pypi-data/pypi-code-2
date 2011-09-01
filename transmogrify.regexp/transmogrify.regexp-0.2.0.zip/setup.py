from setuptools import setup, find_packages
import os

setup(
    author='Alex Clark',
    author_email='aclark@aclark.net',
    description='Modify key values via regexp',
    entry_points={
        'z3c.autoinclude.plugin': 'target = transmogrify',
    },
    include_package_data=True,
    long_description=open('README.rst').read() +
        open(os.path.join('docs', 'HISTORY.txt')).read(),
    name='transmogrify.regexp',
    namespace_packages=['transmogrify'],
    packages=find_packages(),
    url='https://github.com/aclark4life/transmogrify.regexp',
    version='0.2.0',
)
