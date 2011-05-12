from setuptools import setup, find_packages
setup(
    name="LinkExchange.Django",
    version="0.1",
    packages=find_packages(exclude=['tests']),
    author="Konstantin Korikov",
    author_email="lostclus@gmail.com",
    url="http://linkexchange.org.ua",
    download_url="http://linkexchange.org.ua/downloads",
    description="Django integration with LinkExchange library",
    long_description="""
    This package contains Django support code for LinkExchange library.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    license = "LGPL",
    install_requires=[
        'LinkExchange>=0.4dev',
        ],
    test_suite='tests',
    tests_require=[
        'phpserialize',
        'Django',
        ],
    entry_points="""
    [linkexchange.multihash_drivers]
    django = linkexchange_django.db_drivers:DjangoMultiHashDriver
    """,
)
