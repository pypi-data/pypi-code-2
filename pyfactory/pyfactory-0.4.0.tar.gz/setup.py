from setuptools import setup, Command
import pyfactory

# Get the long description by reading the README
try:
    readme_content = open("README.rst").read()
except:
    readme_content = ""

# Create the actual setup method
setup(name='pyfactory',
      version=pyfactory.__version__,
      description='Generic model factory framework',
      long_description=readme_content,
      author='Mitchell Hashimoto',
      author_email='mitchell@kiip.me',
      maintainer='Mitchell Hashimoto',
      maintainer_email='mitchell@kiip.me',
      url="https://kiip.github.com/pyfactory/",
      license="MIT License",
      keywords=["factory", "pyfactory", "model"],
      packages=['pyfactory'],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing"]
      )
