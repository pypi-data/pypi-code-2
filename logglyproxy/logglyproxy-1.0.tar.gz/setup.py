import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

version = '1.0'

setup(name='logglyproxy',
      version=version,
      description='A syslog proxy server forwarding messages to Loggly via HTTPS',
      long_description= README + '\n\n' + CHANGES,
      author='Evax Software',
      author_email='contact@evax.fr',
      url='http://www.evax.fr/',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'setuptools',
          'gevent',
          ],
      keywords = ['syslog', 'loggly', 'gevent', 'https'],
      classifiers = [
              "Development Status :: 5 - Production/Stable",
              "Intended Audience :: System Administrators",
              "License :: OSI Approved :: MIT License",
              "Programming Language :: Python",
              "Operating System :: OS Independent",
              "Topic :: System :: Logging",
              "Topic :: Internet :: Log Analysis",
              ],
      entry_points="""
      [console_scripts]
      logglyproxy = logglyproxy.server:main
      """
      )

