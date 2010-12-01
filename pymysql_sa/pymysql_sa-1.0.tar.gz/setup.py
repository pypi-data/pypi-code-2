from setuptools import setup, find_packages

version = '1.0'

setup(name='pymysql_sa',
      version=version,
      description='PyMySQL dialect for SQLAlchemy.',
      long_description="""\
pymysql_sa
==========

This package provides a PyMySQL__ dialect for SQLAlchemy__.

__ http://code.google.com/p/pymysql/
__ http://www.slqalchemy.org

Installation
------------

::

    easy_install pymysql_sa

Usage
-----

PyMySQL is a pure Python MySQL client providing a DB-API to a MySQL database by talking directly to the server via the binary client/server protocol.

You can explicitly use pymysql by changing the 'mysql' part of your engine url to 'pymysql'.

You can also make pymysql the default mysql dialect as follows::

    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()

In this case you don't need to change the engine url.

Being pure Python, PyMySQL is easily patched by gevent__ and the likes to make it cooperative.

__ http://www.gevent.org

""",
      author="Evax Software",
      author_email="contact@evax.fr",
      url = "http://www.evax.fr",
      license='MIT License',
      packages=find_packages(),
      install_requires=[
          "pymysql >= 0.3",
          "SQLAlchemy >= 0.6.4",
      ],
      keywords = ['sqlalchemy', 'pymysql', 'dialect', 'gevent'],
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Topic :: Database :: Front-Ends",
          "Operating System :: OS Independent",
      ],
      test_suite = "pymysql_sa.tests.all_tests",
      entry_points="""
      [sqlalchemy.dialects]
      pymysql = pymysql_sa:base.dialect
      """,
      )

