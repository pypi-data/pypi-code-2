from setuptools import setup, find_packages
import os

version = '0.1'

install_requires = [
          'setuptools',
          # -*- Extra requirements: -*-
      ]
tests_require = [
    'mocker',
]

setup(name='zettwerk.users',
      version=version,
      description="Additional user information for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
      keywords='Zope CMF Plone Users',
      author='Christoph Glaubitz',
      author_email='cg@zettwerk.com',
      url='http://svn.plone.org/svn/collective/zettwerk.users',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zettwerk'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=install_requires + tests_require,
      entry_points="""
      # -*- Entry points: -*-
      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
