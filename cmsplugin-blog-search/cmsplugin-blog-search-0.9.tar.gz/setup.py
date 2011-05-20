from setuptools import setup

setup(name='cmsplugin-blog-search',
      version='0.9',
      description='Searching using language facets for cmsplugin-blog.',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://github.com/fivethreeo/cmsplugin-blog-search/',
      packages = ['cmsplugin_blog_search'],
      install_requires = ['django-cms-facetsearch']
)
