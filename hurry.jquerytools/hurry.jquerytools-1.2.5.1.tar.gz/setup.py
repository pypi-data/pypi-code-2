from setuptools import setup, find_packages
import os

JQUERYTOOLS_VERSION = '1.2.5'
version = '1.2.5.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='hurry.jquerytools',
    url="http://pypi.python.org/hurry.jquerytools",
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
        'py',
        'hurry.jquery',
        'hurry.resource',
        ],
    entry_points={
        'console_scripts': [
            'jquerytoolsprepare = hurry.jquerytools.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.jquerytools.prepare:working_entrypoint',
            ],
        # ALSO grab jquerytools in the separate tag checkout...
        'zest.releaser.releaser.after_checkout': [
            'prepare = hurry.jquerytools.prepare:tag_entrypoint',
            ],
        'hurry.resource.libraries': [
            'jqueryui = hurry.jquerytools:jquerytools_lib',
            ],

        },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
