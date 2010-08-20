import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="auto-translator",
      version=read('VERSION').strip(),
      description="Translates text files using the Google API through a command line or visual(Tk) interface.  Also designed for translation of web2py language files, just put the path and the app do the rest!",
      author="Alfonso de la Guarda Reyes",
      author_email="alfonsodg@gmail.com",
      license="GPL",
      keywords = "translation web2py google",
      url = "http://pypi.python.org/pypi/auto-translator/",
      scripts=["autotranslate.py","gtrans.py","langs.yml"],
      install_requires=["PyYAML"],
      packages = find_packages(),
#      packages=['gtrans'],
#      package_dir={'gtrans': 'gtrans'},
#      package_data={'gtrans': ['gtrans/*.yml']},
#      data_files=[('gtrans',['gtrans/langs.yml'])],
#      include_package_data=True,
      long_description=read('README'),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)
