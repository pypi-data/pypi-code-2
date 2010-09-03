"""NDG XACML ElementTree based Rule Element reader 

NERC DataGrid
"""
__author__ = "P J Kershaw"
__date__ = "16/03/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: rulereader.py 7109 2010-06-28 12:54:57Z pjkersha $"
from ndg.xacml.core.rule import Rule, Effect
from ndg.xacml.core.condition import Condition
from ndg.xacml.core.target import Target
from ndg.xacml.parsers import XMLParseError
from ndg.xacml.parsers.etree import QName
from ndg.xacml.parsers.etree.reader import ETreeAbstractReader
from ndg.xacml.parsers.etree.factory import ReaderFactory


class RuleReader(ETreeAbstractReader):
    '''ElementTree based XACML Rule parser
    
    @cvar TYPE: XACML type to instantiate from parsed object
    @type TYPE: type
    '''
    TYPE = Rule
    
    def __call__(self, obj):
        """Parse rule object
        
        @param obj: input object to parse
        @type obj: ElementTree Element, or stream object
        @return: new XACML expression instance
        @rtype: ndg.xacml.core.rule.Rule derived type 
        @raise XMLParseError: error reading element               
        """
        elem = super(RuleReader, self)._parse(obj)
        
        xacmlType = RuleReader.TYPE
        rule = xacmlType()
        
        localName = QName.getLocalPart(elem.tag)
        if localName != xacmlType.ELEMENT_LOCAL_NAME:
            raise XMLParseError("No \"%s\" element found" % 
                                xacmlType.ELEMENT_LOCAL_NAME)
        
        # Unpack *required* attributes from top-level element
        attributeValues = []
        for attributeName in (xacmlType.RULE_ID_ATTRIB_NAME, 
                              xacmlType.EFFECT_ATTRIB_NAME):
            attributeValue = elem.attrib.get(attributeName)
            if attributeValue is None:
                raise XMLParseError('No "%s" attribute found in "%s" '
                                        'element' %
                                        (attributeName,
                                         xacmlType.ELEMENT_LOCAL_NAME))
                
            attributeValues.append(attributeValue) 
        
        rule.effect = Effect()        
        rule.id, rule.effect.value = attributeValues
            
        # Parse sub-elements
        for childElem in elem:
            localName = QName.getLocalPart(childElem.tag)
            
            if localName == xacmlType.DESCRIPTION_LOCAL_NAME:
                if childElem.text is not None:
                    rule.description = childElem.text.strip()
                    
            elif localName == Condition.ELEMENT_LOCAL_NAME:
                ConditionReader = ReaderFactory.getReader(Condition)
                rule.condition = ConditionReader.parse(childElem)
                                   
            elif localName == Target.ELEMENT_LOCAL_NAME:
                TargetReader = ReaderFactory.getReader(Target)
                rule.target = TargetReader.parse(childElem)
            
            else:
                raise XMLParseError("XACML Rule child element name %r not "
                                    "recognised" % localName)                
                
        return rule