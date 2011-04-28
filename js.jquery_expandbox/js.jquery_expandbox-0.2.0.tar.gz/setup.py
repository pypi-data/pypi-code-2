from setuptools import setup, find_packages
import os

version = '0.2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_expandbox', 'test_jquery.expandbox.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_expandbox',
    version=version,
    description="Fanstatic packaging of jquery.expandBox",
    long_description=long_description,
    classifiers=[],
    keywords='fanstatic, jquery, javascript',
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
            'jquery.expandbox = js.jquery_expandbox:library',
            ],
        },
    )
