# ./pyxb/bundles/opengis/raw/csw_2_0_2.py
# PyXB bindings for NM:c35b4890f3f07f9b39d4250cbebdd4198468ac22
# Generated 2011-09-09 14:19:15.800581 by PyXB version 1.1.3
# Namespace http://www.opengis.net/cat/csw/2.0.2

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9b8fedac-db18-11e0-abb2-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.raw._nsgroup_2

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/cat/csw/2.0.2', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a Python instance."""
    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=Namespace.fallbackNamespace(), location_base=location_base)
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)

from pyxb.bundles.opengis.raw._nsgroup_2 import Record # {http://www.opengis.net/cat/csw/2.0.2}Record
from pyxb.bundles.opengis.raw._nsgroup_2 import SummaryRecord # {http://www.opengis.net/cat/csw/2.0.2}SummaryRecord
from pyxb.bundles.opengis.raw._nsgroup_2 import AbstractRecord # {http://www.opengis.net/cat/csw/2.0.2}AbstractRecord
from pyxb.bundles.opengis.raw._nsgroup_2 import DCMIRecord # {http://www.opengis.net/cat/csw/2.0.2}DCMIRecord
from pyxb.bundles.opengis.raw._nsgroup_2 import BriefRecord # {http://www.opengis.net/cat/csw/2.0.2}BriefRecord
from pyxb.bundles.opengis.raw._nsgroup_2 import AbstractRecordType # {http://www.opengis.net/cat/csw/2.0.2}AbstractRecordType
from pyxb.bundles.opengis.raw._nsgroup_2 import DCMIRecordType # {http://www.opengis.net/cat/csw/2.0.2}DCMIRecordType
from pyxb.bundles.opengis.raw._nsgroup_2 import RecordType # {http://www.opengis.net/cat/csw/2.0.2}RecordType
from pyxb.bundles.opengis.raw._nsgroup_2 import SummaryRecordType # {http://www.opengis.net/cat/csw/2.0.2}SummaryRecordType
from pyxb.bundles.opengis.raw._nsgroup_2 import EmptyType # {http://www.opengis.net/cat/csw/2.0.2}EmptyType
from pyxb.bundles.opengis.raw._nsgroup_2 import BriefRecordType # {http://www.opengis.net/cat/csw/2.0.2}BriefRecordType
