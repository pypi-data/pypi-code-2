from distutils.core import setup

setup(
    name = 'django-crypto',
    packages = ['django_crypto'],
    version = '0.1.0',
    description = 'Simple 2-way crypto functions for use with Django.',
    author='Matt Snider',
    author_email='msnider@votizen.com',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)