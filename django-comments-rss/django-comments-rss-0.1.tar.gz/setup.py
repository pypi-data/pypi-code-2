from setuptools import setup, find_packages

setup(name='django-comments-rss',
      version='0.1',
      author='Remigijus Jarmalavicius',
      author_email='remigijus@jarmalavicius.lt',
      packages=find_packages(),
      url='http://www.jarmalavicius.lt',
      license='BSD',
      description='RSS channel for django.contrib.comments. Designed for every content type.',
      long_description=open('README.rst').read(),
      )

