from distutils.core import setup


version = __import__('i18nurls').__VERSION__

setup(
    name='django-i18nurls',
    version=version,
    author='Orne Brocaar',
    author_email='info@brocaar.com',
    url='http://bitbucket.org/brocaar/django-i18nurls',
    description='Translate URL patterns and prefix URLs with language-code.',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=[
        'i18nurls',
        'i18nurls.tests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
