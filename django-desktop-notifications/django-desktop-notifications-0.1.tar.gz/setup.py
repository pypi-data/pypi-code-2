#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    'Django>=1.3',
]

try:
    __import__('uuid')
except ImportError:
    # Older versions of Python did not include uuid
    install_requires.append('uuid')

setup(
    name='django-desktop-notifications',
    version='0.1',
    author='Laurent Coustet',
    author_email='ed@zehome.com',
    url='http://code.google.com/django-desktop-notifications/',
    description = 'Django / NodeJS / Chrome / websocket ultra fast desktop notifications',
    packages=find_packages(exclude="demo"),
    zip_safe=False,
    install_requires=install_requires,
    #tests_require=tests_require,
    #test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
		'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
