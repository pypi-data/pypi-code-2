from setuptools import setup
import jira

setup(name='jira',
      version=jira.__version__,
      description='Client for Jira (over XML/RPC)',
      author='Miki Tebeka',
      author_email='miki.tebeka@gmail.com',
      license='MIT',
      url='https://bitbucket.org/tebeka/jira/src',
      py_modules=['jira'],
)
