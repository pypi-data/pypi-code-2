"""
  >>> from five.grok.ftests.view.resource import *

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  We can access to our CSS file:

  >>> browser.open("http://localhost/++resource++five.grok.ftests.view/style.css")
  >>> print browser.contents
  body {
     color: green;
  }
  >>> print browser.headers['content-type']
  text/css; charset=iso-8859-15

  And the template file:

  >>> browser.open("http://localhost/++resource++five.grok.ftests.view/template.pt")
  >>> print browser.contents
  <tal:test>This template should be considered as a file.</tal:test>
  >>> print browser.headers['content-type']
  text/html; charset=iso-8859-15

  Set a content, and ask the view on it. In a view, you should be able
  to get the resource URL:

  >>> id = getRootFolder()._setObject("manfred", Mammoth(id='manfred'))
  >>> browser.open("http://localhost/manfred")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello I a mammoth!</h1>
  <a href="http://localhost/manfred/++resource++five.grok.ftests.view/style.css">A link to some style for life!</a>
  </body>
  </html>

  We can use exists on resource files:

  >>> browser.open("http://localhost/manfred/exists")
  >>> print browser.contents
  <html>
  <body>
  <span>Test succeed</span>
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>
  >>> browser.open("http://localhost/manfred/existsandtraverse")
  >>> print browser.contents
  <html>
  <body>
  <span>Test succeed</span>
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>


"""
from five import grok

class Mammoth(grok.Model):

    def __init__(self, id):
        super(Mammoth, self).__init__(id)
        self.id = id            # XXX: if you don't have an id, the
                                # link will be bad. Maybe this should
                                # happens by default.

class Index(grok.View):
    pass

index = grok.PageTemplate("""\
<html>
<body>
<h1>Hello I a mammoth!</h1>
<a href="#"
   tal:attributes="href view/static/style.css">A link to some style for life!</a>
</body>
</html>
""")


class Exists(grok.View):
    pass

exists = grok.PageTemplate("""\
<html>
<body>
<span
   tal:condition="exists: view/static/style.css">Test succeed</span>
<span
   tal:condition="exists: view/static/nonexistant.css">Test failed</span>
</body>
</html>
""")


class ExistsAndTraverse(grok.View):
    pass

existsandtraverse = grok.PageTemplate("""\
<html>
<body>
<span
   tal:condition="exists: context/++resource++five.grok.ftests.view/style.css">Test succeed</span>
<span
   tal:condition="exists: context/++resource++five.grok.ftests.view/nonexistant.css">Test failed</span>
</body>
</html>
""")


