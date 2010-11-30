from distutils.core import setup

setup(
    name='mcs',
    author='Michael Gruenewald',
    author_email='mail@michaelgruenewald.eu',
    description='Monticello repository synchronization tool',
    long_description=open('README').read(),
    license='License :: OSI Approved :: MIT License',
    url='https://bitbucket.org/michaelgruenewald/mcs',
    version='0.3',
    packages=['mcs',],
    requires=['httplib2 (>=0.6.0)',
              'pyparsing'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Archiving :: Mirroring',
    ],
)
