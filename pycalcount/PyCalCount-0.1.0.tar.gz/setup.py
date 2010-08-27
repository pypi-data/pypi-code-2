from distutils.core import setup

setup(
    name='PyCalCount',
    version='0.1.0',
    author='x.seeks',
    author_email='x.seeks@gmail.com',
    packages=['pycalcount'],
    scripts=['bin/pycalcount'],
    url='http://pypi.python.org/pypi/PyCalCount/',
    license='LICENSE.txt',
    description='A basic calorie-counting and meal-logging program.',
    long_description=open('README.txt').read(),
)
