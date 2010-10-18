from setuptools import setup, find_packages

JQUERYUI_VERSION = '1.8.5'
version = '1.8.5.1'
# version named after JQUERYUI_VERSION + .suffix. Can't do this
# automatically as it'd confuse zest.releaser

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.jqueryui',
    version=version,
    description="hurry.resource style resources for jQuery UI.",
    long_description = long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource >= 0.10',
        'hurry.jquery >= 1.4.2.3',
        ],
    entry_points= {
        'console_scripts': [
            'jqueryuiprepare = hurry.jqueryui.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.jqueryui.prepare:working_entrypoint',
            ],
        'zest.releaser.releaser.after_checkout': [
            'prepare = hurry.jqueryui.prepare:tag_entrypoint',
            ],
        'hurry.resource.libraries': [
            'jqueryui = hurry.jqueryui:jqueryui_lib',
            'jqueryui_themes = hurry.jqueryui:jqueryui_themes',

            ],
    },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        'prepare': ['py'],
        },
    )
