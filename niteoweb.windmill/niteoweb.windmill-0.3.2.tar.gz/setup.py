import os.path
from setuptools import setup, find_packages

DIR = os.path.dirname(os.path.abspath(__file__))

setup(name='niteoweb.windmill',
      version='0.3.2',
      description="Plone TestCase integration with Windmill testing",
      long_description=open(os.path.join(DIR, 'README.txt')).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone windmill',
      author='Niteoweb d.o.o.',
      author_email='info@niteoweb.com',
      url='http://www.niteoweb.com/',
      license='GNU GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['niteoweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'windmill',
      ],
      entry_points="""""",
      )
