from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar-django13',
    version=__import__('debug_toolbar').__version__,
    description='A configurable set of panels that display various debug information about the current request/response. Version fully Django 1.3 compatible',
    long_description=open('README.rst').read(),
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    author='Rob Hudson',
    author_email='rob@cogit8.org',
    url='http://github.com/msaelices/django-debug-toolbar/downloads',
    download_url='http://github.com/robhudson/django-debug-toolbar/downloads',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
