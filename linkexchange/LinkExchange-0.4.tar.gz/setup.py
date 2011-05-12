from setuptools import setup, find_packages
setup(
    name="LinkExchange",
    version="0.4",
    packages=find_packages(exclude=["tests"]),
    namespace_packages=['linkexchange'],
    author="Konstantin Korikov",
    author_email="lostclus@gmail.com",
    url="http://linkexchange.org.ua",
    download_url="http://linkexchange.org.ua/downloads",
    description="Universal link exchange service client library",
    long_description="""
    This library helps to integrate various link exchange services into python
    powered website. Features includes support for Sape.ru and LinkFeed.ru
    services, flexible link grouping and formatting facilities.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    license="LGPL",
    install_requires=[
        'setuptools',
        ],
    test_suite='tests',
    tests_require=['phpserialize'],
    entry_points="""
    [linkexchange.clients]
    sape = linkexchange.clients.sape:SapeClient
    sape_context = linkexchange.clients.sape:SapeContextClient
    sape_articles = linkexchange.clients.sape:SapeArticlesClient
    linkfeed = linkexchange.clients.linkfeed:LinkFeedClient
    trustlink = linkexchange.clients.trustlink:TrustLinkClient

    [linkexchange.multihash_drivers]
    mem = linkexchange.db_drivers:MemMultiHashDriver
    shelve = linkexchange.db_drivers:ShelveMultiHashDriver

    [linkexchange.formatters]
    inline = linkexchange.formatters:InlineFormatter
    list = linkexchange.formatters:ListFormatter

    [console_scripts]
    lxrefresh = linkexchange.commands.lxrefresh:main
    """,
)
