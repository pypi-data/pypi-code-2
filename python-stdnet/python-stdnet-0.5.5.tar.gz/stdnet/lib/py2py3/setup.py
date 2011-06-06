from distutils.core import setup

import py2py3

setup(
    name='py2py3',
    author=py2py3.__author__,
    author_email=py2py3.__contact__,
    version=py2py3.__version__,
    url=py2py3.__homepage__,
    py_modules=['py2py3'],
    description=py2py3.__doc__,
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ]
)