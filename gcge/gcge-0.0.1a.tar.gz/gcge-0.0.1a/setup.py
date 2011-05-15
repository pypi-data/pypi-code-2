from setuptools import setup, find_packages

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

setup(
    name='gcge',
    version='0.0.1a',
    description='generic card game engine',
    long_description=long_description,
    author='Gerg Morin',
    author_email='gerglion@gmail.com',
    url='http://code.google.com/p/gcge/',
    install_requires=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    classifiers = [
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
