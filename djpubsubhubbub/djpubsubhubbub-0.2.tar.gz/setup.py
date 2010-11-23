from distutils.core import setup

long_description = open('README').read()

setup(
    name='djpubsubhubbub',
    version=__import__('djpubsubhubbub').__version__,
    package_dir={'djpubsubhubbub': 'djpubsubhubbub'},
    packages=['djpubsubhubbub',],
    description='Django PubSubHubbub App',
    author='Peter Sanchez',
    author_email='petersanchez@gmail.com',
    license='BSD License',
    url='http://bitbucket.org/petersanchez/djpubsubhubbub/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
