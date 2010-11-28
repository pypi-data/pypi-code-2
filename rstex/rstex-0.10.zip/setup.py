from setuptools import setup
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "License :: OSI Approved :: BSD License"
    ]

setup(
    name="rstex",
    version="0.10",
    description="An extension of docutils' rst2latex with inline math, "
                "equations, references, and raw latex",
    license="BSD License",
    keywords="restructuredtext rst docutils latex tex math rst2latex",
    scripts=["src/rstex.py"],
    author="Marcin Cieslik",
    author_email="mpc4p@virginia.edu",
    url="http://muralab.org/rstex",
    zip_safe=False,
    install_requires=["setuptools", "docutils"]
)
