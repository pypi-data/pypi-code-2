from setuptools import setup, find_packages

setup(name='blueprint_io',
      version='0.1.0',
      description='centralized blueprint service client',
      author='Richard Crowley',
      author_email='richard@devstructure.com',
      url='http://devstructure.com/',
      packages=find_packages(),
      install_requires=['blueprint >= 3.0.5'],
      license='BSD',
      zip_safe=False)
