from setuptools import setup, find_packages

__version__ = '0.1.2'

setup(
    name = 'insight-bertrpc',
    license='MIT',
    version = __version__,
    description = 'BERT-RPC Library',
    author = 'Team Insight',
    author_email = 'jordan.bach@reelfx.com',
    url = 'https://github.com/teaminsight/python-bertrpc',
    packages = ['bertrpc'],
    install_requires = ["erlastic", "bert"],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
