"""\
A simple benchmark to compare different ways of generating safe HTML.

When run on Python 2.5 I get this:

::

    $ ~/env/bin/python  html_escape_benchmark.py 
    0.265987157822 0.0220429897308
    Efficiency of plain literal:  8.28723834314 %
    10.2524540424 1.4699549675 0.863940000534
    Efficiency of plain literal:  14.3375913846 %
    Same output:  True

This tells me that combining a ``webhelpers.html.literal`` object is more than
10x slower than creating an ordinary Unicode object and that combining a
``literal`` with 5 unicode objects is only 6x slower than the same code written
with ``HTMLFragment``. The final line shows that both output the same result.

These benchmarks are the justification for including ``HTMLFragment`` with
BareNecessitites.

Their are commented out versions of alternative implementations and 
approcahes.
"""

from webhelpers.html import HTML, literal
import time
from  cgi import escape
from bn import HTMLFragment

#class HTMLFragment(list):
#    def write(self, string):
#        list.write(self, string.replace(u'&',u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;'))
#    def safe(self, string):
#        list.write(self, string)

#from StringIO import StringIO
#
#class HTMLFragment(StringIO):
#    def __str__(self):
#        return StringIO.getvalue(self)
#    def write(self, string):
#        StringIO.write(self, string.replace(u'&',u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;'))
#    def safe(self, string):
#        StringIO.write(self, string)

runs = 10000

a = time.time()
for x in range(runs):
    s=literal(u'<form action="/action" method="post"><table>')
b = time.time()
for x in range(runs):
    s=u'<form action="/action" method="post"><table>'
c = time.time()

print b-a, c-b
print "Efficiency of plain literal: ", (100*(c-b))/(b-a), '%'

a = time.time()
for x in range(runs):
    sa=unicode(literal(u'<form action="/action" method="post"><table>')+\
        (u'<b>')+\
        (u'<c>')+\
        (u'<d>')+\
        (u'<e>')+\
        (u'<f>'))
b = time.time()
for x in range(runs):
    o=HTMLFragment()
    o.safe(u'<form action="/action" method="post"><table>')
    o.write(u'<b>')
    o.write(u'<c>')
    o.write(u'<d>')
    o.write(u'<e>')
    o.write(u'<f>')
    sb = o.getvalue()
c = time.time()
for x in range(runs):
    '<form action="/action" method="post"><table>'+\
        ('<b>'.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;'))+\
        ('<c>'.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;'))+\
        ('<d>'.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;'))+\
        ('<e>'.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;'))+\
        ('<f>'.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;'))
d = time.time()

print b-a, c-b, d-c
print "Efficiency of plain literal: ", (100*(c-b))/(b-a), '%'

print "Same output: ", sa==sb
