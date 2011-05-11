from setuptools import setup

setup(name='django-cms-facetsearch',
      version='0.9',
      description='Searching using language facets for django-cms pages and plugins.',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://github.com/fivethreeo/django-cms-facetsearch/',
      packages = ['cms_facetsearch'],
      package_data={'cms_facetsearch': ['templates/search/*.html']}
)
