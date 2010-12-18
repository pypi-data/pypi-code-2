from setuptools import setup

setup(
    name = 'django-hs-sessions',
    version = __import__('hs_sessions').__version__,
    url = 'http://bitbucket.org/dchaplinsky/django-hs-sessions',
    license = 'MIT',
    author = 'Dmitry Chaplinsky',
    author_email='chaplinsky.dmitry@gmail.com',
    packages = ["hs_sessions"],
    install_requires = ['python-handler-socket',],
    description = 'HandlerSocket session backend for django',
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