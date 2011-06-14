from setuptools import setup, find_packages
import sys, os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import mdown

setup(
    name="mezzanine-mdown",
    version=mdown.__version__,
    url="https://bitbucket.org/onelson/mezzanine-mdown/",
    author="Owen Nelson",
    author_email="onelson@gmail.com",
    license="MIT",
    description="Markdown for RichText content in Mezzanine.",
    long_description=open('README').read(),
    keywords="django, mezzanine, markdown, wmd",
    packages=find_packages(),
    setup_requires=("setuptools"),
    install_requires=("setuptools", "mezzanine>=0.11.3", "markdown",),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: "
                              "Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",],
    zip_safe=False,
    include_package_data=True,
)

