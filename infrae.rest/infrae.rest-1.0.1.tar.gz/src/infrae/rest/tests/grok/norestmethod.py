"""

  You can't define a REST view with no methods:

   >>> grok('infrae.rest.tests.grok.norestmethod')
   Traceback (most recent call last):
     ...
   GrokError: REST component testempty doesn't define any REST method

"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import REST


class TestEmpty(REST):
    grok.context(Folder)
