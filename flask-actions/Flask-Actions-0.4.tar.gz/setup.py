"""
Flask-Actions
-------------

custom actions for flask

Links
`````

* `documentation <http://packages.python.org/Flask-Actions>`_
* `development version
  <http://bitbucket.org/youngking/flask-actions/get/tip.gz#egg=Flask-Actions-dev>`_


"""
from setuptools import setup


setup(
    name='Flask-Actions',
    version='0.4',
    url='http://blog.flyzen.com',
    license='BSD',
    author='Young King',
    author_email='yanckin@gmail.com',
    description='custom actions for flask to help manage your application',
    long_description=__doc__,
    packages=['flaskext','flaskext.actions'],
    namespace_packages=['flaskext'],
    test_suite='nose.collector',
    tests_require=['Nose'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug'
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
