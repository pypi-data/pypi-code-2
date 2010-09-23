from setuptools import setup, find_packages
import os

JQPLOT_VERSION = '0.9.7'
version = '0.9.7.1'
# Name version after JQPLOT_VERSION + .suffix


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n')

setup(
    name='hurry.jqplot',
    version=version,
    description="hurry.resource style resources for jqPlot.",
    url = "http://github.com/jmichiel/hurry.jqplot",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Jeroen Michiel',
    author_email='jmichiel@yahoo.com',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource > 0.2',
        'hurry.jquery > 1.3.2',
        ],
    entry_points={
        'console_scripts': [
            'jqplotprepare = hurry.jqplot.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.jqplot.prepare:entrypoint',
            ],
        # ALSO grab hurry.raphael in the separate tag checkout...
        'zest.releaser.releaser.middle': [
            'prepare = hurry.jqplot.prepare:entrypoint',
            ],
        },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
