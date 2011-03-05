from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name = "liquidjango",
        version = "0.2.1",
        packages = find_packages('src'),
        package_dir = {'': 'src'},
        url = 'https://bitbucket.org/adalovelace/liquidjango/overview',
        license = "gpl3",
        author = "Tatiana de la O",
        author_email = "acracia@cryptodrunks.net",
        description = "an interface to control a radio with liquidsoap",
        long_description = read('README'),
        install_requires = [ 'distribute' ],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP',
            ]
)
