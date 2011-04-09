
try:
    from setuptools import setup
except:
    from distutils.core import setup

from gefr import gefr_version    

setup(
    name="gefr",
    version=gefr_version,
    author="Sun Ning",
    author_email="classicning@gmail.com",
    url="https://bitbucket.org/sunng/gefr",
    description="A very simple wsgi-compatible http server, based on Java infrastructure",
    license='bsd',
    py_modules=['gefr.core', 'gefr.wsgi', 'gefr.backends.soldat', 'gefr.backends.mina'],
    long_description="""
    gefr is a simple wsgi-compatible http server, running on the Java infrastructure, soldat.
    
    """,
    classifiers=['Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Java',
        'Environment :: Web Environment',
        'Operating System :: POSIX']
)


