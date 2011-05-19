try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='pydataframe',
    version='0.1.2',
    packages=['pydataframe',],
    license='BSD',
    url='http://code.google.com/p/pydataframe/',
    author='Florian Finkernagel',
    author_email='finkernagel@coonabibba.de',
    long_description=open('README.txt').read(),
    install_requires=[
        'numpy>1.3',
        ]
)
