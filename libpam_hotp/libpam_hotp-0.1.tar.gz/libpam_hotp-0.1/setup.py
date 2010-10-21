from setuptools import setup
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
    name='libpam_hotp',
    version='0.1',
    description=('Pam module to authenticate users using HOTP token.'),
    long_description=ldesc,
    keywords='pam hotp token otp',
    author='Antoine Millet',
    author_email='antoine@inaps.org',
    license='GPL', 
    data_files = [('/lib/security/', ['pam_hotp.py'])],
    url='http://libpam-hotp.idevelop.org',
    classifiers=[
		'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
    ],
)
