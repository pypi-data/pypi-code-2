import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    'WebOb',
]

if sys.version_info < (2, 7):
    install_requires.append('ArgParse')

setup(
    name='Milla',
    version='0.1.1',
    description='Lightweight WSGI framework for web applications',
    author='Dustin C. Hatch',
    author_email='admiralnemo@gmail.com',
    url='http://bitbucket.org/AdmiralNemo/milla',
    license='APACHE-2',
    classifiers=[
         'Development Status :: 3 - Alpha',
         'Environment :: Web Environment',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=install_requires,
    packages=find_packages('src', exclude=['distribute_setup']),
    package_dir={'': 'src'},
    entry_points={
        'milla.request_validator': [
            'default = milla.auth:RequestValidator'
        ],
        'console_scripts': [
            'milla-cli = milla.cli:main'
        ],
    }
)
