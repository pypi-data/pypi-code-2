
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages 
import glob, os.path, sys


# Read long description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Path check
def which(command):
    percorso = os.getenv("PATH")
    directories = percorso.split(os.pathsep)
    for path_dir in directories:
        real_dir = os.path.expanduser(path_dir)
        try:
            lista_dir = os.listdir(real_dir)
        except OSError:
            lista_dir = []
        if os.path.exists(real_dir) and command in lista_dir:
            return os.path.join(real_dir, command)
    return None


# Look for script files
lscr = glob.glob(os.path.join('Scripts', 'XSPEC*'))
lscrex = []
for i in lscr:
    if os.path.splitext(i)[1] == '':
        lscrex.append(i)


# python
print "Python version %s" % (sys.version)
pvl = sys.version.split()[0].split('.')
if int(pvl[0]) != 2 or int(pvl[1]) < 3:
    print "Python version should be 2.x with x at least 3."


import XSF
durl = 'http://www.me.oa-brera.inaf.it/utenti/covino/XSPECfeeder-%s.tar.gz' % XSF.__version__


setup(
    name='XSPECfeeder', 
    version=XSF.__version__, 
    description='Scientific data management', 
    packages = find_packages('.'),
    include_package_data = True,
    long_description="""Simple tool to convert optical/high energy data to be used by XSPEC.
     
    Try XSPECfeeder -l for instructions or XSPECfeeder -h for help.""",
    author='Jure Japelj, Stefano Covino', 
    author_email='stefano.covino@brera.inaf.it', 
    url='http://www.me.oa-brera.inaf.it/utenti/covino', 
    download_url=durl,    
    install_requires=['atpy','pyfits','asciitable','numpy'],
    scripts=lscrex,
    classifiers=[ 
        'Development Status :: 5 - Production/Stable', 
        'Environment :: Console', 
        'Intended Audience :: Science/Research', 
        'License :: Freely Distributable', 
        'Operating System :: MacOS :: MacOS X', 
        'Operating System :: POSIX', 
        'Programming Language :: Python :: 2', 
        'Topic :: Scientific/Engineering :: Astronomy', 
        ], 
    ) 


# nose