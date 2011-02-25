from setuptools import setup, find_packages


setup(
    name='django-vhost',
    version='0.17',
    url='https://bitbucket.org/djangostars/django-vhost',
    license='BSD',
    author='Vasyl Dizhak',
    author_email='vasyl.dizhak@djangostars.com',
    maintainer='Vasyl Dizhak',
    maintainer_email='vasyl.dizhak@djangostars.com',
    description='Generates virtual host configuration files for apache and nginx',
    long_description='Generates virtual host configuration files for apache and nginx',
    keywords='django nginx apache fastcgi wsgi',
    packages=[
        'django_vhost',
        'django_vhost.management',
        'django_vhost.management.commands'
    ],
    # packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Django'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
