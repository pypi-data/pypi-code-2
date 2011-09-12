from setuptools import setup, find_packages
import os

setup(
    name='django-appskel',
    version='1.0a',
    description='App for building reusable app skeletons with testsr',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read(),
    author='Oyvind Saltvik',
    author_email='oyvind.saltvik@gmail.com',
    url='http://github.com/fivethreeo/django-appskel/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django'
    ],
    scripts = ['djangoappskel/bin/django-appskel.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Jinja2']
)
