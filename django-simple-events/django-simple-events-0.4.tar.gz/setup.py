from setuptools import setup, find_packages
from os.path import join, dirname

def dump(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
        name='django-simple-events',
        version='0.4',

        packages=find_packages(),
        install_requires=('',''),
        author='Unai Zalakain',
        author_email='contact@unaizalakain.info',

        keywords='',
        description='',
        long_description=dump('README'),

        license='GPLv3',
        )
    
