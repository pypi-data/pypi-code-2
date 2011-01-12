"""
html5witch offers Pythonic HTML5 generation based on xmlwitch. BSD-licensed.

Usage
`````

::

    >>> import html5witch
    >>> doc = html5witch.Builder()
    >>> with doc.html:
    ...     with doc.head:
    ...        doc.title('Title')
    ...     with doc.body:
    ...        doc.p('Hello World')
    ...        with doc.form(action="/", method="post"):
    ...            doc.input(type="input", name="my_input_field")
    ... 
    >>> print(doc)
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Title</title>
      </head>
      <body>
        <p>Hello World</p>
        <form action="/" method="post">
          <input type="input" name="my_input_field">
        </form>
      </body>
    </html>

Setup
`````

::

    $ pip install html5witch # or
    $ easy_install html5witch # or
    $ cd xmlwitch-0.2.1; python setup.py install
    $ cd html5witch-0.2.1; python setup.py install

Links
`````

* `Full documentation <http://jonasgalvez.com.br/Software/HTML5Witch.html>`_
* `Development repository <http://github.com/galvez/html5witch/>`_
* `Author's website <http://jonasgalvez.com.br/>`_

"""

from setuptools import find_packages, setup

setup(
    name = 'html5witch',
    version = '0.2.1',
    url = 'http://jonasgalvez.com.br/Software/HTML5Witch.html',
    license = 'BSD',
    author = "Jonas Galvez",
    author_email = "jonasgalvez@gmail.com",
    description = "html5witch offers Pythonic HTML5 generation based on xmlwitch",
    long_description = __doc__,
    py_modules = ['html5witch'],
    install_requires = ['xmlwitch>=0.2'],
    platforms = 'Python 2.5 and later',
    classifiers = [
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)