from setuptools import setup, find_packages
import os

version = '0.9.7'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_jqote2', 'test_jquery.jqote2.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_jqote2',
    version=version,
    description="Fanstatic packaging of jquery.jqote2",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Stephane Klein',
    author_email='stephane@harobed.org',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jquery'
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery.jqote2 = js.jquery_jqote2:library',
            ],
        },
    )
