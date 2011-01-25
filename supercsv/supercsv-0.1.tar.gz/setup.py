from os.path import abspath, dirname, join as pjoin
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


fn = abspath(pjoin(dirname(__file__), 'README.rst'))
fp = open(fn, 'r')
long_description = fp.read()
fp.close()

setup(
    name='supercsv',
    version='0.1',
    license='PSF',
    description='csv unicode',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=[
        'supercsv',
    ],
    platforms='any',
    # we don't want eggs
    zip_safe=False,
)

