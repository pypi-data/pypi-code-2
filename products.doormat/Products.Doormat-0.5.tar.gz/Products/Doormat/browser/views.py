from plone.memoize.instance import memoize

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

class DoormatView(BrowserView):
    """
    """

    def getDoormatTitle(self):
        """
        """
        title = ''
        if self.context.getShowTitle():
            title = self.context.Title()
        return title
         
    def getDoormatData(self):
        """ Return a dictionary like this:
        data = [
            {   'column_title: 'Column One',
                'column_sections: [
                {   'section_title': 'De Oosterpoort',
                    'section_links': [
                        {   'link_title': 'Some Title',
                            'link_url': 'http://some.whe.re',
                            'link_class': 'external-link',
                            'content': 'html content',
                            },
                        ]
                    },
                ]
            },
        ]
        """
        doormat = self.context
        data = []
        # Fetch Columns
        for column_brain in doormat.getFolderContents():
            column_dict = {
                'column_title': column_brain.Title,
                'show_title': column_brain.getShowTitle,
                }
            column_sections = []
            section_brains = column_brain.getObject().getFolderContents()

            # Fetch Categories from Column
            for section_brain in section_brains:
                section_dict = {
                    'section_title': section_brain.Title,
                    'show_title': section_brain.getShowTitle,
                    }
                section_links = []
                brains = section_brain.getObject().getFolderContents()

                # Loop over all link object in category
                for brain in brains:
                    # Use the link item's title, not that of the linked content
                    title = brain.Title
                    item = brain.getObject()
                    text = ''
                    url = ''
                    link_class = ''

                    if brain.portal_type == 'DoormatReference':
                        linked_item = item.getInternal_link()
                        if not linked_item:
                            continue
                        url = linked_item.absolute_url()
                    elif brain.portal_type == "Link":
                        # Link is an Archetypes link
                        url = brain.getRemoteUrl
                        link_class = "external-link"
                    elif brain.portal_type == "Document":
                        text = item.getText()
                    
                    if not (text or url):
                        continue

                    link_dict = {
                        'content': text, 
                        'link_url': url, 
                        'link_title': title,
                        'link_class': link_class,
                        }
                    section_links.append(link_dict)
                section_dict['section_links'] = section_links
                column_sections.append(section_dict)
            column_dict['column_sections'] = column_sections
            data.append(column_dict)
        return data



##code-section module-footer #fill in your manual code here
##/code-section module-footer


