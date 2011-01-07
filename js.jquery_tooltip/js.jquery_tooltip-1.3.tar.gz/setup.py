from setuptools import setup, find_packages
import os

version = '1.3'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_tooltip', 'test_jquery_tooltip.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_tooltip',
    version=version,
    description="fanstatic jQuery tooltip.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    extras_require = dict(
        test=['pytest >= 2.0'],
        ),
    entry_points={
        'fanstatic.libraries': [
            'jquery_tooltip = js.jquery_tooltip:library',
            ],
        },
    )
