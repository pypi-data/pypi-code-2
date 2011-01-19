from setuptools import setup, find_packages
import sys

# quick hack, will probably do something better later.
requirements = ["configobj", "byteplay==0.2"]
if sys.version_info[1] < 7:
    requirements.append("importlib")

# this is a quick hack again... I hope they might just stop :-)


setup(name='pydenji',
      description='Dependency Injection Toolkit',
      # add byteplay as soon as it works.
      version='0.5.5',
      install_requires=requirements,
      long_description="""
      Dependency Injection Toolkit.

      Enables easy dependency injection and declarative configuration for
      Python projects. While inspired by projects such as Spring Framework
      or Ruby's DIM, it is designed to be unobtrusive. It doesn't require
      modification in your business code to be employed; it can just be used in
      the outer layer, where configuration is actually needed.

      Small additional tools to help with configuration management are provided
      and can be used when and where are really fit.

      """,
      author='Alan Franzoni',
      license='APL 2.0',
      keywords='dependency injection inversion control ioc container',
      author_email='username@franzoni.eu',
      url='http://pydenji.franzoni.eu',
      download_url='http://pypi.python.org/simple/pydenji',
      packages=find_packages(exclude=["test"]),
      setup_requires=["setuptools_hg"],
     )
