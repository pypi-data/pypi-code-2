from setuptools import setup, find_packages
import os

JQUERYTOOLS_VERSION = '1.2.4'
version = '1.2.4'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='hurry.jquerytools',
    version=version,
    description="hurry.resource style resources for jquerytools.",
    long_description=long_description,
    classifiers=[],
    keywords='jQuery jquerytools Zope3 Popup',
    author='Christian Klinger',
    author_email='cklinger@novareto.de',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.jquery == 1.4.2.1',
        'hurry.resource == 0.4.1',
        ],
    entry_points={
        'console_scripts': [
            'jquerytoolsprepare = hurry.jquerytools.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.jquerytools.prepare:entrypoint',
            ],
        # ALSO grab jquerytools in the separate tag checkout...
        'zest.releaser.releaser.middle': [
            'prepare = hurry.jquerytools.prepare:entrypoint',
            ],
        },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
