from setuptools import setup, find_packages
import os

version = '0.2'

setup(
    name='babble.demo',
    version=version,
    description="Creates a demo Babble instant messaging setup for Plone",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Framework :: Plone",
    "Programming Language :: Python",
    ],
    keywords='babble messaging demo plone',
    author='JC Brand',
    author_email='brand@syslab.com',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['babble'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'actionbar.babble',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    setup_requires=["PasteScript"],
    paster_plugins=["ZopeSkel"],
    )
