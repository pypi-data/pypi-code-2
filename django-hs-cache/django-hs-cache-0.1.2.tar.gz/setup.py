from setuptools import setup

setup(
    name = 'django-hs-cache',
    version = __import__('hs_cache').__version__,
    url = 'http://bitbucket.org/dchaplinsky/django-hs-cache',
    license = 'MIT',
    author = 'Dmitry Chaplinsky',
    author_email='chaplinsky.dmitry@gmail.com',
    packages = ["hs_cache"],
    install_requires = ['python-handler-socket',],
    description = 'HandlerSocket cache backend for Django',
    platforms = 'any',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database',
        'Framework :: Django',
    ],
)