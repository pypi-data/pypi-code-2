import os
from setuptools import setup

test_require = ['plone.app.testing']

setup(
    name='Products.PloneServicesCenter',
    version='0.2.6',
    description='A hub for information about the service options and deployments for Plone',
    long_description=open("README.txt").read() + '\n' +
        open(os.path.join("docs", "HISTORY.txt")).read(),
    maintainer='Alex Clark',
    maintainer_email='aclark@aclark.net',
    url='http://svn.plone.org/svn/collective/Products.PloneServicesCenter/trunk',
    install_requires=[
        'Plone',
        'Products.ArchAddOn',
        ],
    test_require=test_require,
    extras_require={'test': test_require},
    classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
