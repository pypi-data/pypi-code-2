from setuptools import setup, find_packages

description = """Reusable Django application that helps you to deliver
fresh media files, even if their expiry period is really long. To do this,
the application provides a template tag that adds a small hash to the URL
of each served file. This hash depends on the file metadata or content,
so if it is changed, the hash will be changed too.
"""

setup(
    name='django-fresh-media',
    version='0.65',
    url='https://bitbucket.org/djangostars/django-fresh-media',
    license='BSD',
    author='Roman Osipenko',
    author_email='roman.osipenko@djangostars.com',
    description=description,
    long_description='Application to add hashes to media files',
    keywords='django media hash browser',
    packages=['fresh_media', 'fresh_media/templatetags'],
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
