from setuptools import setup, find_packages
import os


__name__ = 'Products.BugzScout'
__namespace__ = ['Products']
__version__ = '1.0a2'


setup(
    name=__name__,
    version=__version__,
    author='WebLion Group, Penn State University',
    author_email='support@weblion.psu.edu',
    description="FogBugz Plone integration using BugzScout.",
    # XXX need to add a stub file to point to the built sphinx docs
    long_description='\n\n'.join([
        open('README.txt').read(),
        open(os.path.join('doc','changes.rst')).read(),
        ]),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        ],
    keywords='weblion fogbugz',
    url='https://weblion.psu.edu/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'bootstrap.py']),
    namespace_packages=__namespace__,
    install_requires=[
        'setuptools',
        'plone.app.registry',
        ],
    extras_require=dict(test=['plone.app.testing']),
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin] 
    target = plone 
    """,
    include_package_data=True,
    zip_safe=False,
    )
