from setuptools import setup, find_packages
import sys, os

version = '0.3'

tests_require = [
    'nose',
    'tw.rum',
    'BeautifulSoup',
    'WebTest',
]

if sys.version_info[:2] == (2, 4):
    tests_require.append("pysqlite")



setup(name='RumAlchemy',
    version=version,
    description="RESTful web interface generator for SQLAlchemy mapped classes using rum and ToscaWidgets",
    long_description="""\
    """,
    classifiers=[],
    keywords='toscawidgets sqlalchemy rum',
    author='Alberto Valverde Gonzalez, Michael Brickenstein',
    author_email='info@python-rum.org',
    url='http://python-rum.org/',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    test_suite = "nose.collector",
    zip_safe=False,
    install_requires=[
        'rum >= 0.3dev-20090708',
        'SQLAlchemy >= 0.5.0beta3',
        'zope.sqlalchemy',
    ],
    tests_require = tests_require,
    entry_points="""
    [rum.repositoryfactory]
    sqlalchemy = rumalchemy:SARepositoryFactory

    [console_scripts]
    rumalchemy = rumalchemy.command:rumalchemy
    """,
    )
