from setuptools import setup, find_packages
setup(
    name="LinkExchange.TurboGears",
    version="0.1",
    packages=find_packages(exclude=['tests']),
    namespace_packages=['linkexchange'],
    author="Konstantin Korikov",
    author_email="lostclus@gmail.com",
    url="http://linkexchange.org.ua",
    download_url="http://linkexchange.org.ua/downloads",
    description="TurboGears 1.x integration with LinkExchange library",
    long_description="""
    This package contains TurboGears 1.x support code for LinkExchange library.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    license="LGPL",
    install_requires=[
        'LinkExchange>=0.4dev',
        'TurboGears>=1.0,<2.0',
        ],
    test_suite='tests',
    tests_require=[
        'phpserialize',
        'TurboGears>=1.0,<2.0',
        'SQLObject>=0.10.1',
        'pysqlite',
        ],
)
