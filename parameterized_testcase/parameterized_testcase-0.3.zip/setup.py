from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'parameterized_testcase',
    version = '0.3',
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Austin Bingham',
    author_email = 'austin.bingham@gmail.com',
    description = 'Create unittest-compatible parameterized testcases.',
    license = 'MIT',
    keywords = 'unittest',
    url = 'http://code.google.com/p/parameterized-testcase/',
    downloadurl = 'http://pypi.python.org/pypi/parameterized_testcase',
    # long_description
    # zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
        ],
    platforms='any',
    include_package_data=True,
    )

