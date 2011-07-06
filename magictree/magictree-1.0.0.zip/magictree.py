'''
magictree.py

2011-07-06 - Daren Thomas: initial version

Creating tree structures like those used for HTML and XML should be dead easy.
The xml.etree.ElementTree library goes quite far in creating a simple to use library
for creating and modifying such structures. I'd like to go a step further, building
on top of ElementTree:

    from magictree import html, head, title, body, h1, p
    doc = html(
            head(
              title('Chapter 1: Greeting')),
            body(
              h1('Chapter 1: Greeting'),
              p('Hello, world!')))

    from xml.etree import ElementTree as et    
    et.dump(doc)

--> results in this: (added some whitespace for formatting)

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
import sys
from xml.etree import ElementTree as et

class ElementFactoryFactory(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.elementFactories = {} 
    def __getattr__(self, name):
        if not name in self.elementFactories:
            self.__createElementFactory(name)
        return self.elementFactories[name]

    def __createElementFactory(self, name):
        '''creates an element factory for a given name'''
        def factory(*children, **attributes):
            element = et.Element(name, attributes)
            for child in children: 
                if isinstance(child, str) or isinstance(child, unicode):
                   element.text = child 
                else:
                    element.append(child)
            return element
        self.elementFactories[name] = factory

# wrap this module in the element factory factory
sys.modules[__name__] = ElementFactoryFactory(sys.modules[__name__])
