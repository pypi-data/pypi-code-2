"""
Flask-Enterprise
================

Enterprise capabilities for Flask.  Supports SOAP, WSDL and XMLRPC.

Links:

* `Flask-Enterprise Documentation <http://massive.immersedcode.org/2011/staging/projects/default/python/flask-enterprise/>`_
* `Flask <http://flask.pocoo.org>`_
"""
from setuptools import setup


setup(
    name='Flask-Enterprise',
    version='1.0',
    url='http://massive.immersedcode.org/2011/staging/projects/default/python/flask-enterprise/',
    license='CDDL',
    author='Massive of Rock Inc.',
    description='Enterprise capabilities for Flask',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.3',
        'soaplib',
        'suds'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
