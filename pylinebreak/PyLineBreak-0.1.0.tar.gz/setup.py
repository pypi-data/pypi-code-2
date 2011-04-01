from distutils.core import setup

setup(
    name='PyLineBreak',
    version='0.1.0',
    author='x.seeks',
    author_email='x.seeks@gmail.com',
    packages=['pylinebreak',],
    scripts=['bin/pylinebreak'],
    url='http://pypi.python.org/pypi/PyLineBreak',
    license='GPL3, see LICENSE.txt',
    description='Formats text files with line breaks to fit inside 80 chars',
    long_description=open('README.txt').read(),
)
