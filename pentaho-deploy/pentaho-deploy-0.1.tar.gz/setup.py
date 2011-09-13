#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='pentaho-deploy',
    version=0.1,
    description=('Command line tools to help to install, '
                 'deploy and configure Pentaho Softwares on '
                 'Linux servers.'),
    packages=find_packages(),
    author='Sergio Oliveira',
    author_email='seocam@seocam.com',
    scripts=['scripts/pentaho-deploy.sh'],
    package_data={'pentahodeploy': ['upstart-jobs/*']},
    
    # We require an old version of URLGrabber in order to avoid the
    #   dependency of Py-cURL instroduced on newer versions
    install_requires=['fabric>=1.2', 'urlgrabber==3.1.0'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ]
)
