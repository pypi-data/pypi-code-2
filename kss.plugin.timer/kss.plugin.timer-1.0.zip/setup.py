from setuptools import setup, find_packages
import os

def read_package_file(filename):
    file = open(os.path.join('kss', 'plugin', 'timer', filename))
    text = file.read().strip()
    file.close()
    return text


readme = read_package_file('README.txt')
history = read_package_file('HISTORY.txt')

long_description = readme + '\n\n' + history
version = '1.0'

setup(
    name='kss.plugin.timer',
    version=version,
    description="Timer plugin for KSS",
    long_description=long_description,
    author="Guido Wesdorp and Zest software",
    author_email="info@zestsoftware.nl",
    url="http://pypi.python.org/pypi/kss.plugin.timer",
    install_requires=["kss.base", "setuptools"],
    packages=find_packages(),
    namespace_packages=['kss', 'kss.plugin'],
    include_package_data=True,
    test_suite = 'kss.plugin.timer.tests.test_suite',
    entry_points={
        'kss.plugin': [
            'kss.plugin.timer=kss.plugin.timer.config:Kss.plugin.timer'
            ],
        },
)
