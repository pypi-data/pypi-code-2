# ./pyxb/bundles/opengis/raw/_smil20.py
# PyXB bindings for NM:21ae4a2357cfe334f6a0ce0b0ea28423d22a1453
# Generated 2011-09-09 14:18:49.475903 by PyXB version 1.1.3
# Namespace http://www.w3.org/2001/SMIL20/ [xmlns:smil20]

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:8ad340a4-db18-11e0-8861-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.raw._nsgroup_

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/SMIL20/', create_if_missing=True)
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

from pyxb.bundles.opengis.raw._nsgroup_ import animateMotion # {http://www.w3.org/2001/SMIL20/}animateMotion
from pyxb.bundles.opengis.raw._nsgroup_ import animate # {http://www.w3.org/2001/SMIL20/}animate
from pyxb.bundles.opengis.raw._nsgroup_ import animateColor # {http://www.w3.org/2001/SMIL20/}animateColor
from pyxb.bundles.opengis.raw._nsgroup_ import set_ as set # {http://www.w3.org/2001/SMIL20/}set
from pyxb.bundles.opengis.raw._nsgroup_ import syncBehaviorType # {http://www.w3.org/2001/SMIL20/}syncBehaviorType
from pyxb.bundles.opengis.raw._nsgroup_ import fillDefaultType # {http://www.w3.org/2001/SMIL20/}fillDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON # None
from pyxb.bundles.opengis.raw._nsgroup_ import setPrototype # {http://www.w3.org/2001/SMIL20/}setPrototype
from pyxb.bundles.opengis.raw._nsgroup_ import restartTimingType # {http://www.w3.org/2001/SMIL20/}restartTimingType
from pyxb.bundles.opengis.raw._nsgroup_ import restartDefaultType # {http://www.w3.org/2001/SMIL20/}restartDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import fillTimingAttrsType # {http://www.w3.org/2001/SMIL20/}fillTimingAttrsType
from pyxb.bundles.opengis.raw._nsgroup_ import syncBehaviorDefaultType # {http://www.w3.org/2001/SMIL20/}syncBehaviorDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_ # None
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_2 # None
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_3 # None
from pyxb.bundles.opengis.raw._nsgroup_ import animateMotionPrototype # {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
from pyxb.bundles.opengis.raw._nsgroup_ import nonNegativeDecimalType # {http://www.w3.org/2001/SMIL20/}nonNegativeDecimalType
from pyxb.bundles.opengis.raw._nsgroup_ import animatePrototype # {http://www.w3.org/2001/SMIL20/}animatePrototype
from pyxb.bundles.opengis.raw._nsgroup_ import animateColorPrototype # {http://www.w3.org/2001/SMIL20/}animateColorPrototype
