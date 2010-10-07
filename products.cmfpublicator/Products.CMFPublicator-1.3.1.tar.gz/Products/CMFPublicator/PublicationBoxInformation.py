##############################################################################
#
# Copyright (c) 2004 Dinheiro Vivo <www.dinheirovivo.com.br>
#                    by Jean Rodrigo Ferri <jeanrodrigoferri@yahoo.com.br>
# 
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
##############################################################################

#from Globals import InitializeClass // Deprecated
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName

try: # New CMF
    from Products.CMFCore.permissions import ReviewPortalContent, View
except: # Old CMF
    from Products.CMFCore.CMFCorePermissions import ReviewPortalContent, View

from Products.CMFPublicator import MessageFactory as _

class PublicationBoxInformation(SimpleItem):
    """Represent a publication box with the box information and all items
    information like CMF DublinCore metadata.

    Items metadata are stored in a dictionary format.
    """

    __allow_access_to_unprotected_subobjects__ = 1

    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        """Inicialize publication box properties.
        """

        self.edit(**kwargs)


    security.declareProtected(ReviewPortalContent, 'edit')
    def edit(self, **kwargs):
        """Inicialize or update the publication box properties.
        """

        if not self.getId():
            id = kwargs.get('id')
            if id is not None:
                if id:
                    self.id = str(id)
                else:
                    raise ValueError(_(u"A valid id is required."))

        title = kwargs.get('title')
        if title is not None:
            if title:
                self.title = str(title)
            else:
                raise ValueError(_(u"A name is required."))

        content_type = kwargs.get('content_type')
        if content_type is not None:
            if content_type:
                self.content_type = list(content_type)
            else:
                raise ValueError(_(u"At list one content type is required."))

        icon_url = kwargs.get('icon_url')
        if icon_url is not None:
            self.icon_url = str(icon_url)

        n_items = kwargs.get('n_items')
        if n_items is not None:
            if n_items:
                self.n_items = int(n_items)
            else:
                raise ValueError(_(u"A value to number of items is required."))

        n_searched_items = kwargs.get('n_searched_items')
        if n_searched_items is not None:
            if n_searched_items:
                self.n_searched_items = int(n_searched_items)
            else:
                raise ValueError(_(u"A value to number of searched items is required."))

        search_states = kwargs.get('search_states')
        if search_states is not None:
            if search_states:
                self.search_states = list(search_states)
            else:
                raise ValueError(_(u"At list one search workflow state is required."))

        with_image = kwargs.get('with_image')
        if with_image is not None:
            self.with_image = int(with_image)

        images_folder = kwargs.get('images_folder')
        if images_folder is not None:
            self.images_folder = str(images_folder)

        image_states = kwargs.get('image_states')
        if image_states is not None:
            self.image_states = list(image_states)

        box_width = kwargs.get('box_width')
        if box_width is not None:
            self.box_width = str(box_width)

        box_height = kwargs.get('box_height')
        if box_height is not None:
            self.box_height = str(box_height)

        visible = kwargs.get('visible')
        if visible is not None:
            self.visible = int(visible)

        items = kwargs.get('items')
        if items is not None:
            self.setItems(items)


    security.declarePrivate('clone')
    def clone(self):
        """Return a newly-created publication box just like this.
        """

        return self.__class__(id=self.id,
                              title=self.title,
                              content_type=self.content_type,
                              icon_url=self.icon_url,
                              n_items=self.n_items,
                              n_searched_items=self.n_searched_items,
                              search_states=self.search_states,
                              with_image=self.with_image,
                              images_folder=self.images_folder,
                              image_states=self.image_states,
                              box_width=self.box_width,
                              box_height=self.box_height,
                              visible=self.visible,
                              items=self.items)


    security.declarePrivate('extract')
    def extract(self):
        """Return all Publication Box data in a dictionary format.
        """

        pb_dict = {}

        pb_dict['id'] = self.getId()
        pb_dict['name'] = self.getName()
        pb_dict['content_type'] = self.getContent_type()
        pb_dict['icon_url'] = self.getIcon_url()
        pb_dict['n_items'] = self.getN_items()
        pb_dict['n_searched_items'] = self.getN_searched_items()
        pb_dict['search_states'] = self.getSearch_states()
        pb_dict['with_image'] = self.getWith_image()
        pb_dict['images_folder'] = self.getImages_folder()
        pb_dict['image_states'] = self.getImage_states()
        pb_dict['box_width'] = self.getBox_width()
        pb_dict['box_height'] = self.getBox_height()
        pb_dict['visible'] = self.getVisible()
        pb_dict['items'] = self.getItems()

        return pb_dict


    security.declareProtected(View, 'getName')
    def getName(self):
        """Return the title of this Publication Box.
        """

        return self.title

    security.declareProtected(View, 'getContent_type')
    def getContent_type(self):
        """Return the content types presented in this Publication Box.
        """

        return self.content_type[:]

    security.declareProtected(View, 'getIcon_url')
    def getIcon_url(self):
        """Return the icon URL of this Publication Box.
        """

        return self.icon_url

    security.declareProtected(View, 'getN_items')
    def getN_items(self):
        """Return the number of items that will be stored in this Publication
        Box.
        """

        return self.n_items

    security.declareProtected(View, 'getN_searched_items')
    def getN_searched_items(self):
        """Return the number of items that will be searched and displayed in
        the Publication Box selection interface.
        """

        return self.n_searched_items

    security.declareProtected(View, 'getSearch_states')
    def getSearch_states(self):
        """Return the workflow states which items are searched.
        """

        return self.search_states[:]

    security.declareProtected(View, 'getWith_image')
    def getWith_image(self):
        """Return whether the Publication Box have an image.
        """

        return self.with_image

    security.declareProtected(View, 'getImages_folder')
    def getImages_folder(self):
        """Return the images folder to each item.
        """

        return self.images_folder

    security.declareProtected(View, 'getImage_states')
    def getImage_states(self):
        """Return the workflow states which images are searched.
        """

        return self.image_states[:]

    security.declareProtected(View, 'getBox_width')
    def getBox_width(self):
        """Return the Publication Box portlet width.
        """

        return self.box_width

    security.declareProtected(View, 'getBox_height')
    def getBox_height(self):
        """Return the Publication Box portlet height.
        """

        return self.box_height

    security.declareProtected(View, 'getVisible')
    def getVisible(self):
        """Return whether this Publication Box is visible.
        """

        return self.visible

    security.declareProtected(View, 'getItems')
    def getItems(self):
        """Return a copy of the items list of this Publication Box.
        """

        return self.items[:]

    security.declareProtected(ReviewPortalContent, 'setItems')
    def setItems(self, items):
        """Store the items of this Publication Box.
        """

        self.items = list(items)

    security.declareProtected(ReviewPortalContent, 'resetItems')
    def resetItems(self):
        """Reset all items of this Publication Box.
        """

        self.setItems(items=[])

    security.declareProtected(ReviewPortalContent, 'updateItems')
    def updateItems(self, portal_object):
        """Update all items of this Publication Box.

        Portal object is needed because this object don't use acquisition.
        """

        items = self.getItems()

        if items:
            box_id = self.getId()
            items_list = []
            properties = {}
            index = 0

            for item in items:
                properties['item_%s_%d' % (box_id, index)] = item.get('RelativeURL', '')
                properties['image_url_%s_%d' % (box_id, index)] = item.get('ImageURL', '')
                properties['new_window_%s_%d' % (box_id, index)] = item.get('NewWindow', '')

                pb_dict = self._extractItem(properties, index, portal_object)
                items_list.append(pb_dict)

                index += 1

            self.setItems(items_list)


    security.declareProtected(ReviewPortalContent, 'changeItems')
    def changeItems(self, properties, portal_object):
        """Change all items of this Publication Box.

        Portal object is needed because this object don't use acquisition.
        """

        box_id = self.getId()
        items_list = []

        for index in range(self.getN_items()):
            pb_dict = self._extractItem(properties, index, portal_object)
            items_list.append(pb_dict)

        self.setItems(items_list)


    security.declarePrivate('_extractPBItems')
    def _extractItem(self, properties, index, portal_object):
        """Extract the information of the items of a publication box from the
        funky form properties.
        """

        item_metadata = {}
        box_id = self.getId()

        RelativeURL = str(properties.get('item_%s_%d' % (box_id, index), ''))
        item_metadata['RelativeURL'] = RelativeURL
        item_metadata['ImageURL'] = str(properties.get('image_url_%s_%d' % (box_id, index), ''))
        item_metadata['NewWindow'] = str(properties.get('new_window_%s_%d' % (box_id, index), ''))

        if not RelativeURL:
            object = None
        else:
            try:
                object = portal_object.restrictedTraverse(RelativeURL)
            except:
                raise ValueError('An inconsistent path has been passed in item restrictedTraverse.')

        # Default DublinCore properties
        try:
            item_metadata['Title'] = object.Title()
            item_metadata['Creator'] = object.Creator()
            item_metadata['Subject'] = object.Subject()
            item_metadata['Description'] = object.Description()
            item_metadata['Contributors'] = object.Contributors()
            item_metadata['Date'] = object.Date()
            item_metadata['CreationDate'] = object.CreationDate()
            item_metadata['EffectiveDate'] = object.EffectiveDate()
            item_metadata['ExpirationDate'] = object.ExpirationDate()
            item_metadata['ModificationDate'] = object.ModificationDate()
            item_metadata['Type'] = object.Type()
            item_metadata['Format'] = object.Format()
            item_metadata['Identifier'] = object.Identifier()
            item_metadata['Language'] = object.Language()
            item_metadata['Rights'] = object.Rights()
        except:
            item_metadata['Title'] = ''
            item_metadata['Creator'] = ''
            item_metadata['Subject'] = None
            item_metadata['Description'] = ''
            item_metadata['Contributors'] = None
            item_metadata['Date'] = None
            item_metadata['CreationDate'] = None
            item_metadata['EffectiveDate'] = None
            item_metadata['ExpirationDate'] = None
            item_metadata['ModificationDate'] = None
            item_metadata['Type'] = ''
            item_metadata['Format'] = ''
            item_metadata['Identifier'] = ''
            item_metadata['Language'] = ''
            item_metadata['Rights'] = ''

        # Link property
        try:
            item_metadata['RemoteUrl'] = object.getRemoteUrl()
        except:
            item_metadata['RemoteUrl'] = ''

        # Event property
        try:
            item_metadata['start'] = object.start()
            item_metadata['end'] = object.end()
        except:
            item_metadata['start'] = None
            item_metadata['end'] = None

        # Other properties
        try:
            portal_url = getToolByName(portal_object, 'portal_url', None)
            item_metadata['RelativeContentURL'] = portal_url.getRelativeContentURL(object)
        except:
            item_metadata['RelativeContentURL'] = ''

        # Zope properties
        try:
            item_metadata['Id'] = object.getId()
        except:
            item_metadata['Id'] = ''
        try:
            item_metadata['Icon'] = object.getIcon(relative_to_portal=1)
        except:
            item_metadata['Icon'] = ''

        # Customize the getPublicatorItemInfo Python Script skin to return another
        # needed metadatas. Ex.: Specific metadata Archetypes content.
        try:
            if object is not None:
                external_info = portal_object.getPublicatorItemInfo(object)
            else:
                # It need return a dictionary with empty keys.
                external_info = portal_object.getPublicatorItemInfo()
            item_metadata.update(external_info)
        except:
            raise ValueError(_(u"Error in getPublicatorItemInfo method. It need returns a dictionary."))

        return item_metadata


InitializeClass(PublicationBoxInformation)