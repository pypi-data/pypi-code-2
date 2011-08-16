from distutils.core import setup

setup(
    name='meteo',
    version='0.1.0',
    author='H. Wouters',
    author_email='hendrikwout@gmail.com',
    packages=['meteo'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://www.nowebsite.com',
    license='LICENSE.txt',
    description='Meteorological procedures.',
    long_description=open('README.txt').read(),
)
