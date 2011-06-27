from setuptools import setup, find_packages

pages = [ 'button.html','example.html','tkinter.html' ]

setup(
      name="PyDocu",
      version="v0.0.1a",
      description="PyDocu is a lightweight documentation system, very flexible and very fast!",
      author="Maik Woehl",
      author_email="maik.woehl@web.de",
      url="http://www.daemon-tuts.de/pypackages/pydocu",
      packages=find_packages(),
      data_files=['tkhelp.db', 'README', 'index.html', 'favicon.ico', 'CHANGE',
                    pages, 'js/jquery-1.6.min.js', 'css/favicon.ico', 'tkhelp.css'],
      license="GNU General Public License (GP)L",
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)'
                   ],
      )