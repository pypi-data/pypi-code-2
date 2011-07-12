import os
from setuptools import setup

readme = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme).read()

setup(
    name = "pygdb2",
    version = "0.1",
    author = "Antonio Cuni",
    author_email = "anto.cuni@gmail.com",
    url = "https://bitbucket.org/antocuni/pygdb2/",
    license = "BSD",
    platforms = ["unix", "linux"],
    packages = ["pygdb2"],
    description = "Control GDB from within the Python program being debugged",
    long_description = long_description,
    )
