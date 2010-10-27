"""pyQPCR: a free software to compute qPCR

pyQPCR is a GUI application written in python that computes quantitative
PCR (QPCR) raw data. Using quantification cycle values extracted from 
QPCR instruments, it uses a proven and universally applicable model to 
give finalized quantification results.
"""
from distutils.core import setup
import glob
import sys

# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Programming Language :: Python :: 2.6
Environment :: X11 Applications :: Qt
License :: OSI Approved :: GNU General Public License (GPL)
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Medical Science Apps.
Operating System :: Microsoft :: Windows
Operating System :: MacOS :: MacOS X
Operating System :: Unix
"""

doclines = __doc__.split("\n")
print doclines[0]

if sys.platform == 'darwin':
    import py2app
    extra_options = dict(
                         setup_requires=['py2app'],
                         app=['direct-run.py']
                         # Cross-platform applications generally expect sys.argv to
                         # be used for opening files.
                        )
    extra_options['options'] = \
           {
         'py2app': {'argv_emulation' : True,
                    'iconfile' : 'logo.icns',
                    'semi_standalone' : 'False',
                    'includes': ['sip', 'PyQt4._qt']
                   }
           }       

elif sys.platform == 'win32':
    import py2exe
    extra_options = dict(
                         setup_requires=['py2exe'],
                         data_files = [(r'mpl-data', 
    glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\*.*')),
                                      (r'mpl-data', 
    [r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
                                      (r'mpl-data\images',
    glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
                                      (r'mpl-data\fonts',
    glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\fonts\*.*')),
    (r'C:\Python26\Microsoft.VC90.CRT.manifest'),
    (r'C:\Python26\DLLs\msvcp90.dll'), (r'C:\Python26\msvcr90.dll')]
                        )
    extra_options['options'] = \
           {
    'py2exe': { "includes" : ["sip", "matplotlib.backends",  
                               "matplotlib.backends.backend_qt4agg",
                               "matplotlib.figure","pylab", "numpy", 
                               "matplotlib.numerix.fft",
                               "matplotlib.numerix.linear_algebra", 
                               "matplotlib.numerix.random_array",
                               "matplotlib.backends.backend_tkagg"],
                'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
                             '_fltkagg', '_gtk', '_gtkcairo', ],
                'dll_excludes': ['libgdk-win32-2.0-0.dll', 'MSVCP90.dll',
                                 'libgobject-2.0-0.dll', 'mswsock.dll',
                                 'powrprof.dll', 'uxTheme.dll',
                                 'tcl84.dll', 'tk84.dll'],
              }
          }
    extra_options['windows'] = [{'script' : 'scripts\qpcr',
                                 'icon_resources': [(1, 'logo.ico')]}]

else:
    import platform
    extra_options = dict(
          data_files=[('share/icons/hicolor/16x16/apps', ['pyQPCR-16.png']), 
                      ('share/icons/hicolor/32x32/apps', ['pyQPCR-32.png']), 
                      ('share/applications', ['pyQPCR.desktop'])] \
                        )
    if platform.dist()[0] in ('fedora', 'redhat'):
        extra_options['options'] = \
                {
                'bdist_rpm': { 
                    'requires': ['python-matplotlib', 'PyQt4', 'scipy'],
                    'distribution_name': 'fedora'
                             },
                'install': {'optimize': '1', 'prefix' : '/usr'}
                } 
    elif platform.dist()[0] == 'SuSe':
        extra_options['options'] = \
                {
                'bdist_rpm': { 
                    'requires': ['python-matplotlib', 'python-qt4', 'python-scipy'],
                    'distribution_name': 'opensuse'
                             },
                'install': {'prefix': '/usr'}
                } 

setup(name='pyQPCR',
      version='0.7',
      description=doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description="\n".join(doclines[2:]),
      author='Thomas Gastine',
      author_email='thomas.gastine@wanadoo.fr',
      url='http://pyqpcr.sourceforge.net',
      license='GPLv3',
      platforms=['any'],
      packages=['pyQPCR', 'pyQPCR.dialogs', 'pyQPCR.utils', 'pyQPCR.widgets'],
      scripts=['scripts/qpcr'],
      **extra_options
      )

if sys.platform == 'darwin':
    import os
    print "cp qt.conf dist/pyQPCR.app/Contents/Resources"
    os.system("cp qt.conf dist/pyQPCR.app/Contents/Resources")
