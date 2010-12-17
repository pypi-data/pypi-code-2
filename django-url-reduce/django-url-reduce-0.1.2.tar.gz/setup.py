from setuptools import setup, find_packages

setup(
    name                    = 'django-url-reduce',
    version                 = '0.1.2',
    description             = 'A Django pluggable app that automatically generates and injects shortlinks into your webpages.',
    author                  = 'Kieran Lynn',
    author_email            = 'kieran@octothorpstudio.com',
    license                 = open('LICENSE').read(),
    url                     = 'https://github.com/octothorp/django-url-reduce',
    download_url            = 'https://github.com/octothorp/django-url-reduce/downloads',
    packages                = find_packages(),
    include_package_data    = True,
    zip_safe                = True,
    classifiers             = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)