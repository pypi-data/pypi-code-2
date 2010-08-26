from distutils.core import setup

setup(name = 'stations2playlist',
      version = '0.1',
      author = 'Costin Stroie',
      author_email = 'costinstroie@eridu.eu.org',
      scripts = ['stations2playlist.py'],
      url = 'http://pypi.python.org/pypi/stations2playlist/',
      license = 'GPL',
      description = 'Create a playlist with all stations of a radio such as SKY.fm or Digitally Imported',
      long_description = open('README', 'rb').read(),
      classifiers = ['Classifier: Development Status :: 4 - Beta',
                     'Classifier: Environment :: Console','Classifier: Intended Audience :: End Users/Desktop',
                     'Classifier: License :: OSI Approved :: GNU General Public License (GPL)',
                     'Classifier: Operating System :: OS Independent',
                     'Classifier: Programming Language :: Python',
                     'Classifier: Programming Language :: Python :: 2',
                     'Classifier: Programming Language :: Python :: 2.6',
                     'Classifier: Topic :: Multimedia :: Sound/Audio']
)
# vim: set ft=python ai ts=4 sts=4 et sw=4 sta nowrap nu :
