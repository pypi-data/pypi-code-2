from distutils.core import setup

long_description = open('README.txt').read()

setup(
    name='zerigodns',
    version=__import__('zerigodns').__version__,
    package_dir={'zerigodns': 'zerigodns'},
    packages=['zerigodns',],
    description='Python package to interface with Zerigo DNS API.',
    author='Peter Sanchez',
    author_email='petersanchez@gmail.com',
    license='BSD License',
    url='http://bitbucket.org/petersanchez/zerigodns/',
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
