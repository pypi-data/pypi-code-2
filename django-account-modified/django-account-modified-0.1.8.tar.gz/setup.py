from setuptools import setup

setup(
    version = '0.1.8',
    description = 'Django application for registration and authentication, modified',
    author = 'Pavel Zhukov',
    author_email = 'gelios@gmail.com',
    url = 'http://bitbucket.org/zeus/django-account/',
    name = 'django-account-modified',

    packages = ['account'],

    license = "BSD",
    keywords = "django application registration",
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
