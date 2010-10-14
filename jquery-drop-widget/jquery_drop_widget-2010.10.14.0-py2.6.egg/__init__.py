"""
jQuery Drop Widget

by Geoff Howland  <geoff AT ge10f DOT com>

Creates HTML "widgets" (trees, lists, accordions, auto-reloading images,
popups, etc), fully formed with data injected, wrapped to be updated
automatically by RPC, and with all the proper JS needed to instantiate or update
the widget whether it is on page load, or updating a loaded page via RPC.

Drop Widgets must return their result in a render.Output() object.

This makes all Drop Widgets interchangable.  Drop Widgets must produce a body,
that when invoked on page load with the JS and CSS scripts, will create a
working widget on all major current browsers, and fall through to older browser
support.

This is initially accomplished by using jQuery examples that already work and do
this, but more work may need to be done in the future if any widgets specialize.

Also, all widgets must either be wrapped in a DIV or SPAN tag with an ID that
will be updated by RPC, and is the same ID as the template key, so that
data can be updated automatically with RPC, or by some other mechanism must
automatically update on RPC after a DIV/SPAN tag with the same ID as the
template key passed in for initial templating.  This is confusion, so here is
an example:

<div id="some_dynamic_table">%(some_dynamic_table)s</div>

In dropSTAR, this is how I do templating, and RPC-based dynamic page updating.

The "body" key of the Drop Widget result will be inserted into the
"%(some_dynamic_table)s" template area (JS/CSS/Scripts go into their respective
HEAD areas), and the page is rendered on load.

On RPC mechanism, an RPC call is made, which return a Python Dictionary, turned
associative array Object() in Javascript, which contains a key
"some_dynamic_table" and also keys for "js_include".  The "some_dynamic_table" key's
value is inserted into the DIV with the id "some_dynamic_table" and then the
"js_include" list is iterated and eval()d, to perform any dynamic operations to bring
the data live or update it.

Typically this is just replacing originally templating data with new data,
and then possibly re-invoking the Javascript instantiation code because we just
stomped on the old code.

This may not work though, and we may need to do something more complex, in which
case the dropSTAR update system will STILL expect to just update the DIV/SPAN
with the ID of "some_dynamic_table" and then run all the "js_include" code snippets,
and then must do clever things like manipulating the hidden data stuffed into
the DIV/SPAN tag to bring the widget to life on the page, as many times as the
RPC mechanism is called.

These are the policies of being a Drop Widget, and if they are kept, will
dramatically reduce the time to build interactive web pages with a variety of
widgets that render easily on page load, and keep updating on interval, or at
user interactive request.
"""

from render import *


def Test():
  print render.Value('value0', 'Bobs your uncle!')



if __name__ == '__main__':
  Test()


