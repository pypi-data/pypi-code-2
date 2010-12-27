from setuptools import setup

setup(
    name = 'python-handler-socket',
    version = __import__('pyhs').__version__,
    url = 'http://bitbucket.org/excieve/pyhs',
    license = 'MIT',
    author = 'Artem Gluvchynsky',
    author_email='excieve@gmail.com',
    packages = ["pyhs"],
    description = open('README.rst').read(),
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
    ],
)
