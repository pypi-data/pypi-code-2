from setuptools import setup, find_packages

__version__ = '0.1.3'

setup(
    name = 'insight-bertrpc',
    license='MIT',
    version = __version__,
    description = 'BERT-RPC Library',
    author = 'Michael J. Russo',
    author_email = 'mjrusso@gmail.com',
    maintainer = 'Jordan Bach',
    maintainer_email='jordanbach@gmail.com',
    url = 'https://github.com/teaminsight/python-bertrpc',
    packages = ['bertrpc'],
    install_requires = ["erlastic", "insight-bert"],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
