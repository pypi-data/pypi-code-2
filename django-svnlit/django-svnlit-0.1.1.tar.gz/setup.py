from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='django-svnlit',
    version='0.1.1',
    license='BSD',

    description="Django-based subversion browser.",
    long_description="""Django-based subversion browser.""",
    keywords='django subversion svn browser',
    url='http://code.google.com/p/django-svnlit/',

    author='Tamas Kemenczy',
    author_email='tamas.kemenczy@gmail.com',

    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ),

    install_required=('pysvn',),
    packages=find_packages(exclude=('ez_setup', 'examples', 'tests')),
)
