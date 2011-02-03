#!/usr/bin/env python
from distutils.core import setup

setup(name='Pweave',
      version='0.13',
      description='Literate programming with reST or LaTeX in Sweave style',
      author='Matti Pastell',
      author_email='matti.pastell@helsinki.fi',
      url='http://mpastell.com/pweave',
      packages=['Pweave'],
      license=['GPL'],
      scripts=['Pweave/Pweave'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Text Processing :: Markup',
        'License :: OSI Approved :: GNU General Public License (GPL)'],
      long_description = """

About Pweave
-------------

Pweave is a literate programming tool for Python that is developed after `Sweave <http://www.stat.uni-muenchen.de/~leisch/Sweave/>`_. Like Sweave it uses the noweb syntax. Pweave is a single python script that is able to weave a python code between <<>>= and @ blocks and include the results in the document. Additionally it can capture matplotlib figures. It supports reST, Sphinx and Latex markup. Pweave is good for creating dynamic reports and tutorials. It can also be used to make websites together with Sphinx or rest2web.

Features:
----------

* **Execute python code** in the chunks and **capture input and ouput** to a literate environment using  either `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ or Latex source. Using reST enables conversion of the documents to several formats (html, latex, pdf, odt).
* **Use hidden code blocks**, i.e. code is executed, but not printed in the output file.
* **Capture matplotlib graphics**.
* **Tested with:** Linux, Mac OS X, Windows Python 2.6.  

Install:
--------

With easy_install:::

  easy_install -U Pweave

Or download the source package and run:::

  python setup.py install

Documentation
-------------

Pweave documentation can be found from the website http://mpastell.com/pweave
"""          

)
