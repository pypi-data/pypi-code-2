__doc__ = """
Manage website copy as a directory of markdown-formatted files. Insert files as copy into your
Django templates.
"""

from setuptools import setup, find_packages
import os
from copyblock import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-copyblock',
    version=".".join(map(str, VERSION)),
    author='Steve Ivy',
    author_email='steve@wallrazer.com',
    description='Manage website copy as a directory of markdown-formatted files. Insert files as copy into your Django templates.',
    license='MIT License',
    packages=['copyblock'],
    keywords='django copy markdown',
    url='http://github.com/sivy/django-copyblock/',
    long_description=readme,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ]
)
