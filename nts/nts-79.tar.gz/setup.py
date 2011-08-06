from setuptools import setup, find_packages
from nts.ntsVersion import version

setup(
    name='nts',
    version=version,
    url='http://www.duke.edu/~dgraham/NTS',
    description='note taking simplified',
    long_description='manage notes using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Office/Business', 
        ],
    packages=['nts'],
    package_data={'nts': ['NTS_32.png', 'NTS_128.png', 'NTS_256.png', 'NTS.ico']},
    py_modules=['ez_setup'],
    scripts=['n.py', 'n.pyw'],
)
