from setuptools import setup
import rstspreadsheet

setup(
    name='rstspreadsheet',
    version=rstspreadsheet.__version__,
    author=rstspreadsheet.__author__,
    author_email='aka.tkf@gmail.com',
    description=(
        'Add the `spreadsheet` directive to reStructuredText '
        'for Docutils and Sphinx'),
    long_description=rstspreadsheet.__doc__,
    license=rstspreadsheet.__license__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ],
    py_modules=['rstspreadsheet'],
    )
