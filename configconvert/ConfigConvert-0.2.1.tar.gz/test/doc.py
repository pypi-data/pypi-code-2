"""\
Doctests for ConfigConvert

You'll need to remove the ``test_data`` directory created each time the tests
are run. You can use a command like this:

::

    $ rm -r test_data/ && ~/env/bin/python doc.py | less

The tests also require NestedRecord to run.

"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)
doctest.testfile('../doc/source/api.rst', optionflags=doctest.ELLIPSIS)



