from setuptools import setup, find_packages
setup(
    name="LinkExchange.Trac",
    version="0.1",
    packages=find_packages(exclude=['tests']),
    namespace_packages=['linkexchange'],
    author="Konstantin Korikov",
    author_email="lostclus@gmail.com",
    url="http://linkexchange.org.ua",
    download_url="http://linkexchange.org.ua/downloads",
    description="Trac integration with LinkExchange library",
    long_description="""
    This package contains Trac support code for LinkExchange library.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Trac',
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
        'Trac>=0.11',
        ],
    test_suite='tests',
    tests_require=[
        'phpserialize',
        'Trac>=0.11',
        'pysqlite',
        ],
    entry_points="""
    [trac.plugins]
    linkexchange = linkexchange.trac.plugin
    """,
)
