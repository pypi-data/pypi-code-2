from setuptools import setup

setup(
    name='merd',
    version='0.2',
    packages=['merd',],
    license='BSD-new',
    long_description=open('README.txt').read(),
    install_requires=['sqlalchemy'],
)
