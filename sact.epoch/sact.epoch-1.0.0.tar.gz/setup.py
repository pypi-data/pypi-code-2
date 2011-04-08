import codecs
from setuptools import setup, find_packages

setup(
    name='sact.epoch',
    version="1.0.0",
    description="",
    long_description=codecs.open("docs/source/overview.rst",  "r", "utf-8").read() + \
                     codecs.open("docs/source/changelog.rst", "r", "utf-8").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
    ],
    keywords='sact time timedelta',
    author='SecurActive SA',
    author_email='valentin.lab@securactive.net',
    url='http://github.com/securactive/sact.epoch',
    license='SecurActive license',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['sact'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'zope.interface',
        'zope.component',
        'pytz',
    ],
    extras_require={'test': [
        'zope.testing',
        # -*- Extra requirements: -*-
        'z3c.testsetup',
    ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
