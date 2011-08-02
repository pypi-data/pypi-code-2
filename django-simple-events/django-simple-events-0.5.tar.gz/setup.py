from setuptools import setup, find_packages
from os.path import join, dirname

def dump(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
        name='django-simple-events',
        version='0.5',

        packages=find_packages(),
        install_requires=('django>=1.2','python-dateutil'),
        author='Unai Zalakain',
        author_email='contact@unaizalakain.info',

        url='http://unaizalakain.info/django-simple-events/',
        keywords='events occurrences daily weekly montly yearly repetitions',
        description='',
        long_description=dump('README.rst'),

        license='GPLv3',
        classifiers=(
            'Development Status :: 5 - Production/Stable',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.6',
            ),
        )
    
