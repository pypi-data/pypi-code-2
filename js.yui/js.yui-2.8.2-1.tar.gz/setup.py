from setuptools import setup, find_packages
import os

version = '2.8.2-1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'yui', 'test_yui.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.yui',
    version=version,
    description='fanstatic YUI',
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
        'setuptools',
        'fanstatic >= 0.11.1',
        ],
    entry_points={
        'console_scripts': [
            'yuiprepare = js.yui.prepare:main',
            ],
        'fanstatic.libraries': [
            'yui = js.yui:yui',
            ],
        },
    )
