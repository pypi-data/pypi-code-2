from setuptools import setup, find_packages

setup(
    name='signal2',
    version='0.2',
    author='Antonio Cuni',
    author_email='anto.cuni@gmail.com',
    py_modules=['signal2'],
    url='http://bitbucket.org/antocuni/signal2',
    license='BSD',
    description='ctypes wrapper around sigaction() and sigqueue()',
    long_description='ctypes wrapper around sigaction() and sigqueue()',
    install_requires=["ctypes_configure",
                      "py" # actually, it's required by ctypes_configure
                      ],
)
