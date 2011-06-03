from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.0'

install_requires = [
    "mako",
    "argparse"
]


setup(name='tacot',
    version=version,
    description="",
    long_description=README + '\n\n' + NEWS,
    keywords='',
    author='Stephane Klein',
    author_email='stephane@harobed.org',
    url='',
    license='',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['tacot=tacot:main']
    }
)
