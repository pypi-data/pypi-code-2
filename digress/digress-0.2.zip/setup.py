from setuptools import setup

setup(
    name="digress",
    version=__import__("digress").__version__,
    description="Python Regression Testing Suite",
    author="Tony Young",
    author_email="rofflwaffls@gmail.com",
    packages=[ "digress", "digress.scm" ]
)