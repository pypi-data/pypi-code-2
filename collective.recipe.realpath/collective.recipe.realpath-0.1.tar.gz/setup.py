from setuptools import setup, find_packages
import os

version = '0.1'

PKG_README = open("README.txt").read()
USAGE_README = open(
    os.path.join(
        'collective', 'recipe', 'realpath', "README.txt"
        )
    ).read()

entry_point = 'collective.recipe.realpath:RealpathRecipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}
tests_require = ['zope.testing', 'zc.buildout']

setup(name='collective.recipe.realpath',
      version=version,
      description="Buildout recipe normalizes directory/path options.",
      long_description="%s\n\n%s" % (PKG_README, USAGE_README),
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: MIT License",
        ],
      keywords='',
      author='Sean Upton',
      author_email='sean.upton@hsc.utah.edu',
      url='http://svn.plone.org/svn/collective',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      tests_require = tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='collective.recipe.realpath.tests.test_docs.test_suite',
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.buildout'
          # -*- Extra requirements: -*-
      ],
      entry_points=entry_points,
      )

