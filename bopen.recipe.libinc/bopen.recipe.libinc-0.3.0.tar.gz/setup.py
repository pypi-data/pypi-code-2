from setuptools import setup, find_packages
import os.path

version = '0.3.0'
name = 'bopen.recipe.libinc'

def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names)).read()

setup(
    name='bopen.recipe.libinc',
    version=version,
    description="zc.buildout recipe that parses compile time options from config scripts",
    long_description= \
        read('README.txt') + \
        '\nDetailed Documentation\n' + \
        '**********************\n\n' + \
        read('bopen', 'recipe', 'libinc', 'README.txt') + \
        '\n',
    classifiers=[
        'Framework :: Buildout',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='development buildout recipe',
    author='Alessandro Amici',
    author_email='a.amici@bopen.eu',
    url='http://www.bopen.eu/open-source/bopen.recipe.libinc',
    license='ZPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bopen', 'bopen.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
    ],
    tests_require = ['zope.testing'],
    test_suite = '%s.tests.test_suite' % name,
    entry_points={
        'zc.buildout' : ['default = %s:LibInc' % name],
    },
)
