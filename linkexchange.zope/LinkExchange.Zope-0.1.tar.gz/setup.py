from setuptools import setup, find_packages
setup(
    name="LinkExchange.Zope",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['linkexchange'],
    author="Konstantin Korikov",
    author_email="lostclus@gmail.com",
    url="http://linkexchange.org.ua",
    download_url="http://linkexchange.org.ua/downloads",
    description="Zope integration with LinkExchange library",
    long_description="""
    This package contains Zope support code for LinkExchange library.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope2',
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
        'LinkExchange>=0.4dev',
        ],
)
