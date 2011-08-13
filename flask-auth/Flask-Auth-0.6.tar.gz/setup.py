"""
Flask-Auth
----------

Database-agnostic extension for Flask to support role-based authentication of
users.

Links
`````

* `documentation <http://packages.python.org/Flask-Auth>`_
* `development version
  <http://bitbucket.org/Shotca/flask-auth/get/tip.gz#egg=Flask-Auth-dev>`_


"""
from setuptools import setup

setup(
    name='Flask-Auth',
    version='0.6',
    url='http://bitbucket.org/Shotca/flask-auth/',
    license='BSD',
    author='Lars de Ridder',
    author_email='shotcage@gmail.com',
    description='Auth extension for Flask.',
    long_description=__doc__,
    packages=[
        'flaskext',
        'flaskext.auth'
    ],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
