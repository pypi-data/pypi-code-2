from setuptools import setup, find_packages


setup(
    name='django-fresh-media',
    version='0.51',
    url='https://bitbucket.org/djangostars/django-fresh-media',
    license='BSD',
    author='Roman Osipenko',
    author_email='roman.osipenko@djangostars.com',
    description='Application to add hashes to media files',
    long_description='Application to add hashes to media files',
    keywords='django media hash browser',
    packages=['fresh_media', 'fresh_media/templatetags'],
    namespace_packages=['fresh_media'],
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
