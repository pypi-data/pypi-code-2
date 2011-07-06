from distutils.core import setup

setup(
        name = 'magictree',
        version = '1.0.0',
        description = 'Easily create ElementTree with automatic Element factories',
        url = 'http://code.google.com/p/pymagictree/',
        author_email = 'daren.thomas@gmx.ch',
        author = 'Daren Thomas',
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.5',
            'Topic :: Text Processing :: Markup :: XML',
            'Topic :: Text Processing :: Markup :: HTML',
            'Operating System :: OS Independent',
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)'
        ],
        py_modules = ['magictree'],
        long_description = '''Creating tree structures like those used for HTML and XML should be dead easy.
The xml.etree.ElementTree library goes quite far in creating a simple to use library
for creating and modifying such structures. I'd like to go a step further, building
on top of ElementTree::

    from magictree import html, head, title, body, h1, p
    doc = html(
            head(
              title('Chapter 1: Greeting')),
            body(
              h1('Chapter 1: Greeting'),
              p('Hello, world!')))

    from xml.etree import ElementTree as et    
    et.dump(doc)

Results in this: (added some whitespace for formatting)

::

    <html>
      <head>
        <title>Chapter 1: Greeting</title>
      </head>
      <body>
        <h1>Chapter 1: Greeting</h1>
        <p>Hello, world!</p>
      </body>
    </html>

This works by replacing this module with a wrapper object in sys.modules that
creates factory functions for elements based on their name.

I used this page as a basis for the hack: http://stackoverflow.com/questions/2447353/getattr-on-a-module
        '''
)
