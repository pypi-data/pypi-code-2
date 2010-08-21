# Copyright (c) 2005-2010 Simplistix Ltd
# See license.txt for license details.

import os
from setuptools import setup,find_packages

package_name = 'Products.MailTemplates'
base_dir = os.path.dirname(__file__)

setup(
    name=package_name,
    version='2.0.0',
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="MailTemplates for Zope 2",
    long_description=open(os.path.join(base_dir,'docs','description.txt')).read(),
    url='http://www.simplistix.co.uk/software/zope/mailtemplates',
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    ],    
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = (
        'Zope2',
        ),
    )
