from distutils.core import setup, Extension
setup(
    name='pyudt',
    version='0.1a',
    ext_modules=[
        Extension('pyudt', ['pyudt.cpp'], libraries=['udt', 'boost_python-py26'])
    ],
)

