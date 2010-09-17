import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "pygora",
    version = "0.0.3",
    packages = find_packages(),
    scripts = ['pygora.py'],
    entry_points = {
        'console_scripts': [
            'pygora = pygora:main'
            ]
        },

    author = "Alfredo Deza",
    author_email = "alfredodeza [at] gmail.com",
    description = "A simple way to get a nice ratio between your test code and your source code",
    license = "MIT",
    keywords = "test code ratio compare count lines",
    url = "http://code.google.com/p/pygora",   

)

