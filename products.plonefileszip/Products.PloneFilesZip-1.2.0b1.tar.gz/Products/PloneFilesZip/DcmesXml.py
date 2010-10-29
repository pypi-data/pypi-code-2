# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Provides the DCMES-XML of DC metadata of a content.
See http://dublincore.org/documents/dcmes-xml/ about the RDF format of DC elements.
See .../Products/Archetypes/ExtensibleMetadata.py about available elements.
Note that we don't provide the "dc:coverage" element since this is not provided by AT/Plone.
$Id: DcmesXml.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from xml.sax.saxutils import escape as basic_xml_escape

HEADER = """<?xml version="1.0" encoding="%(charset)s"?>
<!DOCTYPE rdf:RDF PUBLIC "-//DUBLIN CORE//DCMES DTD 2002/07/31//EN"
    "http://dublincore.org/documents/2002/07/31/dcmes-xml/dcmes-xml-dtd.dtd">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description rdf:about="%(content_url)s">
"""

FOOTER = """
  </rdf:Description>
</rdf:RDF>
"""

DC_ELEMENT = """    <dc:%(name)s xml:lang="%(language)s">%(value)s</dc:%(name)s>"""

class DcmesXML(object):
    """Provides the DCMES-XML of DC metadata of a content"""


    def __init__(self, content, portal, charset):
        """Constructor"""

        self.content = content
        self.portal = portal
        self.charset = charset
        self.language = content.Language()
        return


    def __str__(self):
        """The full DCMES-XML for the content"""

        values = {'charset': self.charset, 'content_url': self.content.absolute_url()}
        return HEADER % values + self.dcElements() + FOOTER


    def dcElements(self):
        """Provides all DC Elements for each non empty metadata"""

        elements = (self.titleElement(), self.creatorElement(), self.subjectElement(),
                    self.descriptionElement(), self.publisherElement(), self.contributorElement(),
                    self.dateElement(), self.typeElement(), self.formatElement(),
                    self.identifierElement(), self.sourceElement(), self.languageElement(),
                    self.relationElement(), self.rightsElement())
        return '\n'.join([e for e in elements if e])


    def titleElement(self):
        """DC title"""

        title = self.content.Title().strip()
        if title:
            return DC_ELEMENT % {'name': 'title',
                                 'language': self.language,
                                 'value': xml_quote(title)}
        else:
            return ''


    def creatorElement(self):
        """DC creator"""

        creator = self.content.Creator().strip()
        if creator:
            return DC_ELEMENT % {'name': 'creator',
                                 'language': self.language,
                                 'value': xml_quote(creator)}
        else:
            return ''


    def subjectElement(self):
        """DC subject (keywords)"""

        keywords = self.content.Subject()
        keywords = [kw for kw in keywords if kw.strip()]
        elements = []
        for kw in keywords:
            elements.append(DC_ELEMENT
                            % {'name': 'subject',
                               'language': self.language,
                               'value': xml_quote(kw)})
        return '\n'.join(elements)


    def descriptionElement(self):
        """DC description"""

        description = self.content.Description().strip()
        description = ' '.join(description.split())
        if description:
            return DC_ELEMENT % {'name': 'description',
                                 'language': self.language,
                                 'value': xml_quote(description)}
        else:
            return ''


    def publisherElement(self):
        """DC publisher"""

        # FIXME: ExtensibleMetadata always returns "No publisher" :(
        # publisher = self.content.Publisher().strip()
        publisher = self.portal.title.strip()
        if publisher:
            return DC_ELEMENT % {'name': 'publisher',
                                 'language': self.language,
                                 'value': xml_quote(publisher)}
        else:
            return ''


    def contributorElement(self):
        """DC contributor(s)"""

        contributors = self.content.listContributors()
        contributors = [c for c in contributors if c.strip()]
        elements = []
        for ctr in contributors:
            elements.append(DC_ELEMENT
                            % {'name': 'contributor',
                               'language': self.language,
                               'value': xml_quote(ctr)})
        return '\n'.join(elements)


    def dateElement(self):
        """DC date"""

        # Note there's always a date
        return DC_ELEMENT % {'name': 'date',
                             'language': self.language,
                             'value': xml_quote(self.content.Date())}


    def typeElement(self):
        """DC type"""

        e_type = self.content.Type().strip()
        if e_type:
            return DC_ELEMENT % {'name': 'type',
                                 'language': self.language,
                                 'value': xml_quote(e_type)}
        else:
            return ''


    def formatElement(self):
        """DC format"""

        # Always haas 'text/plain' default fallback
        return DC_ELEMENT % {'name': 'format',
                             'language': self.language,
                             'value': xml_quote(self.content.Format())}


    def identifierElement(self):
        """DC identifier"""

        # FIXME: MetadataMixin provides the Zope id :(
        # We perfer the UID (assuming we always got an AT based content)
        # identifier = self.content.Identifier()
        return DC_ELEMENT % {'name': 'identifier',
                             'language': self.language,
                             'value': xml_quote(self.content.UID())}


    def sourceElement(self):
        """DC source(s)"""

        # Use UID of references if any
        # FIXME : Should be faster querying the reference_catalog, but not "API safe"
        elements = []
        for target in self.content.getRefs():
            elements.append(DC_ELEMENT
                            % {'name': 'source',
                               'language': self.language,
                               'value': xml_quote(target.UID())})
        return '\n'.join(elements)


    def languageElement(self):
        """DC language"""

        return DC_ELEMENT % {'name': 'language',
                             'language': self.language,
                             'value': self.language}


    def relationElement(self):
        """DC relation(s)"""

        # Use UID of back references if any
        # FIXME : Should be faster querying the reference_catalog, but not "API safe"
        elements = []
        for source in self.content.getRefs():
            elements.append(DC_ELEMENT
                            % {'name': 'relation',
                               'language': self.language,
                               'value': xml_quote(source.UID())})
        return '\n'.join(elements)


    def rightsElement(self):
        """DC rights"""

        rights = self.content.Rights().strip()
        if rights:
            return DC_ELEMENT % {'name': 'rights',
                                 'language': self.language,
                                 'value': xml_quote(rights)}
        else:
            return ''


def xml_quote(str):
    """XML quoting as recommended in http://dublincore.org/documents/dcmes-xml/"""

    return basic_xml_escape(str, {"'": '&apos;', '"': '&quot;'})
