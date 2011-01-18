from setuptools import (setup, find_packages)


setup(
    name="tenpy",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["lxml>=2.2.8"],
    test_suite="tenpy.test",
    author="Naoya Inada",
    author_email="naoina@naniyueni.org",
    description="Template engine which realized the concept of 'Independence of Presentation Logic' for Python 3",
    license="BSD",
    url="https://bitbucket.org/naoina/tenpy",
    classifiers=["Development Status :: 3 - Alpha",
                 "Environment :: Web Environment",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 ]
)
