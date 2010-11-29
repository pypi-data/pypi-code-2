import os, sys
if sys.version_info >= (3,0):
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup

def main():
    setup(
        name='pycmd',
        description='pycmd: tools for managing/searching Python related files.',
        long_description = open('README.txt').read(),
        version='1.0',
        license='MIT license',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel and others',
        author_email='holger at merlinux.eu',
        entry_points = {'console_scripts': [
            "py.cleanup  = pycmd:pycleanup",
            "py.lookup   = pycmd:pylookup",
            "py.countloc = pycmd:pycountloc",
            "py.which   = pycmd:pywhich",
            "py.convert_unittest = pycmd:pyconvert_unittest",
            "py.svnwcrevert= pycmd:pysvnwcrevert",
        ]},
        install_requires=['py>=1.4.0a2',],
        classifiers=['Development Status :: 6 - Mature',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: Utilities',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 3'],
        packages=['pycmd'],
        zip_safe=False,
    )

if __name__ == '__main__':
    main()