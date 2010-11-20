import sys

from setuptools import setup, find_packages

#eyes = __import__('eyes')
readme_file = 'README'

try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "long_description (%s)\n" % readme_file)
    sys.exit(1)

setup(
    name='eyes',
    version='0.4', #eyes.get_version(),
    packages=find_packages(),
    url='http://bitbucket.org/heckj/eyes/',
    author='Joseph Heck',
    author_email='heckj@mac.com',
    description="Eyes is a project to enable quick, simple, and API enabled monitoring and data collection",    
    #vcs.__doc__,
    long_description=long_description,
    zip_safe=False,
    scripts=[], #'bin/vcs'
    test_suite='tests.main',
    install_requires=['Pygments', 
                      'httplib2',
                      'python-dateutil',
                      'simplejson',
                      'unittest2',
                      'unittest-xml-reporting',
                      'Django',
                      'PyRRD',
                      'South',
                      'django-extensions',
                      'django-piston',
                      'elementtree',
                      'logilab-astng',
                      'logilab-common',
                      ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Monitoring',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)


