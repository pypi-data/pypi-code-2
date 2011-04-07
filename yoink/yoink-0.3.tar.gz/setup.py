import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'yoink',
    version = '0.3',
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Austin Bingham',
    author_email = 'austin.bingham@gmail.com',
    description = 'A simple podcast downloader',
    license = 'MIT',
    keywords = 'podcast rss',
    url = 'https://bitbucket.org/abingham/yoink/',

    entry_points = {
        'console_scripts': [
            'yoink = yoink.app:main',
            ],
        },

    install_requires=[
        'baker',
        'decorator',
        'feedparser',
        'ordereddict',
        'threadpool',
        ],
)
