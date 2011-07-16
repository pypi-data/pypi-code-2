from setuptools import setup, find_packages

setup(
    name = 'django-urlauth',
    version = '0.1.7',
    description = 'Django application for user authentication with key in hypertext link',
    url = 'http://bitbucket.org/lorien/django-urlauth/',
    author = 'Grigoriy Petukhov',
    author_email = 'lorien@lorien.name',

    packages = find_packages(),
    include_package_data = True,

    license = "BSD",
    keywords = "django application authentication authorization",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
