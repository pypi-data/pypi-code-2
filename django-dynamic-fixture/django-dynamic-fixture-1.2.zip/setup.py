#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# http://pypi.python.org/pypi/django-dynamic-fixture
# pip install django-dynamic-fixture

setup(name='django-dynamic-fixture',
      version='1.2',
      packages=['django_dynamic_fixture', 'django_dynamic_fixture/tests'],
      install_requires=['django', ],
      url='http://code.google.com/p/django-dynamic-fixture',
      description='A full library to create dynamic model instances for testing purposes.',
      keywords='python django testing fixture',
      license='MIT',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
)
