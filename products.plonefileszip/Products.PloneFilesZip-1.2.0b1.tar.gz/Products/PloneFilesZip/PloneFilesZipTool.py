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
Builds and download a zip file from the current location
$Id: PloneFilesZipTool.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

# Python imports
import os
import tempfile
import zipfile
import types

# Zope imports
from Acquisition import aq_base
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase

try:
    # From CMF 1.5
    from Products.CMFCore import permissions as cmf_permissions
except ImportError, e:
    # Up to CMF 1.4
    from Products.CMFCore import CMFCorePermissions as cmf_permissions

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression

try:
    # From Plone 2.1
    from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
except ImportError, e:
    # Up to Plone 2.0.5
    INonStructuralFolder = None

# Product imports

from registry import GlobalRegistry
from DcmesXml import DcmesXML
from config import *
from policies import PolicyRegistry

_zmi = os.path.join(os.path.dirname(__file__), 'zmi')


class PloneFilesZipTool(PropertyManager, UniqueObject, SimpleItem, ActionProviderBase):
    """Tool to make archive"""

    __implements__ = ActionProviderBase.__implements__

    plone_tool = True
    id = TOOL_ID
    title = "Makes Zip archives with File like objects"
    meta_type = "PloneFilesZipTool"

    _properties = (
        {'id':'title',
         'type': 'string',
         'mode':'w'},
        {'id': 'zippablePortalTypes',
         'label': 'Portal types that export their file (like) fields to ZIP files',
         'type': 'multiple selection',
         'select_variable': 'potentialZippablePortalTypes',
         'mode': 'w'},
        {'id': 'includeRDF',
         'label': 'Include content DC in the ZIP archives?',
         'type': 'boolean',
         'mode': 'w'},
        {'id': 'zipCharset',
         'label': 'Charset of file names in ZIP archives',
         'type': 'string',
         'mode': 'w'},
         {'id': 'innerStructurePolicy',
         'label': 'Inner Structure Policy',
         'type': 'selection',
         'select_variable': 'getInnerStructureZMIVocabulary',
         'mode': 'w'},)

    # Init properties
    zippablePortalTypes = []
    includeRDF = False
    zipCharset = 'cp1252'
    innerStructurePolicy = DEFAULT_ZIP_STRUCTURE_POLICY

    _actions = (
        ActionInformation(
            id='zip',
            title='Download all files from this folder in a ZIP file',
            description='Archive content',
            action=Expression(text='string:files_zip_form'),
            permissions=(cmf_permissions.View, ),
            category='document_actions',
            condition=Expression(text='python:portal.%s.showZipAction(object)' % TOOL_ID),
            visible=1,
            ),)

    manage_options = (
        ({'label' : 'Overview',
          'action' : 'manage_overview'
          },)
        + ActionProviderBase.manage_options
        + PropertyManager.manage_options
        + SimpleItem.manage_options)

    security = ClassSecurityInfo()

    ##
    # ZMI
    ##

    security.declareProtected(cmf_permissions.ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('manage_overview', _zmi)

    security.declarePublic('potentialZippablePortalTypes')
    def potentialZippablePortalTypes(self):
        """All AT based portal types that have one or more field
        that has support in the registry
        """

        portal_types = getToolByName(self, 'portal_types')
        archetype_tool = getToolByName(self, 'archetype_tool')

        # meta2portals = {'meta_type': ['portal_type_1', ...], ...}
        meta2portals = {}
        for type_info in portal_types.listTypeInfo():
            try:
                meta2portals[type_info.Metatype()].append(type_info.getId())
            except KeyError, e:
                meta2portals[type_info.Metatype()] = [type_info.getId()]

        # Installed registered AT types
        installed_at_types = [t for t in archetype_tool.listRegisteredTypes()
                              if t['meta_type'] in meta2portals.keys()]
        zippable_portal_types = []

        # Finding types with compatible fields
        for at_type in installed_at_types:
            for field in at_type['schema'].fields():
                if field.type in GlobalRegistry.listFieldTypes():
                    zippable_portal_types.extend(meta2portals[at_type['meta_type']])
                    break

        # Finding types with registered retrievers
        for at_type in installed_at_types:
            if at_type['meta_type'] in GlobalRegistry.listMetaTypes():
                zippable_portal_types.extend(meta2portals[at_type['meta_type']])

        # Remove potential duplicates
        zippable_portal_types = dict(zip(zippable_portal_types, zippable_portal_types)).keys()
        zippable_portal_types.sort()

        return zippable_portal_types


    security.declarePublic("getInnerStructureZMIVocabulary")
    def getInnerStructureZMIVocabulary(self):
        return PolicyRegistry.getPoliciesZMIVocabulary()

    ###
    # PMI
    ###

    def getInnerStructurePoliciesInfos(self):
        return PolicyRegistry.getPoliciesInfos()

    security.declarePublic('showZipAction')
    def showZipAction(self, content):
        """showZipAction(content) -> boolean
        Wether or not showing the UI to the user"""

        # Useless in non folderish
        if not isFolderish(content):
            return False
        # There should be 1 or more file in...
        files = self.contentBrains(content)
        return not not len(files)


    security.declarePublic('contentBrains')
    def contentBrains(self, content, REQUEST=None):
        """Compatible content objects available from here"""

        if REQUEST is None:
            REQUEST = self.REQUEST
        portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
        portal_catalog = getToolByName(self, 'portal_catalog')
        if portal_quickinstaller.isProductInstalled('LinguaPlone'):
            # If we're in a LinguaPlone stuff, we should show only the local language files
            language = REQUEST.get('LANGUAGE', self.portal_properties.site_properties.default_language)
            file_brains = portal_catalog.searchResults(portal_type=self.zippablePortalTypes,
                                                       path='/'.join(content.getPhysicalPath()),
                                                       language=language)
        else:
            # Don't care about the language
            file_brains = portal_catalog.searchResults(portal_type=self.zippablePortalTypes,
                                                       path='/'.join(content.getPhysicalPath()))
        return file_brains

    security.declarePublic('zipFileName')
    def zipFileName(self, content):
        """FileName to be used"""

        return content.getId() + '.zip'

    ##
    # Public
    ##

    def createTemporaryZipFileFromBrains(self, brains, policy, root_path):
        """
        Create a ZipFile object from brains
        Returns the path of temporary file

        @param brains: List of brains
        @param policy: Policy used to store content in zip
        @param root_path: Prefix removed from brain path to build zip directory
        structure
        """

        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        mimetypes_registry = getToolByName(portal, 'mimetypes_registry')

        # Create temporary file
        fd, path = tempfile.mkstemp('.zippe')
        os.close(fd)

        # out_file = tempfile.TemporaryFile(suffix='.zippe')
        zip = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)

        # Walking the contents
        zip_archive_mapping = dict()

        for brain in brains:
            content = brain.getObject()

            if content is None:
                # FIXME : Log this ghost object
                continue
            try:
                dummy = charset
            except NameError, e:
                charset = content.getCharset()

            content_id = content.getId()
            content_path = portal_url.getRelativeContentURL(content)
            content_relative_path = content_path[len(root_path):]

            container_path = "/".join(tuple(content_path.split("/")[:-1]))

            # Remove potential leading "/"
            if content_relative_path.startswith('/'):
                content_relative_path = content_relative_path.lstrip('/')
            content_relative_path = zipNameEncode(content_relative_path, charset, self.zipCharset)

            # Zipping the DC RDF file
            if self.includeRDF:
                rdf_zip_path = policy.getRdfZipPath(content_relative_path)
                zip.writestr(rdf_zip_path, str(DcmesXML(content, portal, charset)))

            # Zipping "fileable" fields
            retrievers = GlobalRegistry.getRetrieversFor(content)

            for retriever in retrievers:
                filename = retriever.fileName()
                if not os.path.splitext(filename)[1]: # No .ext ending filename?

                    # Add the default extension for that type
                    try:
                        ext = mimetypes_registry.lookup(retriever.mimeType())[0].extensions[0]
                    except IndexError, e:
                        ext = '.dat'
                    ext = ext.split('.')[-1] # ext may be 'xxx' or '*.xxx' (curious MimetypesRegistry behaviour)
                    filename = filename + '.' + ext

                field_relative_path = retriever.relativePathFrom(content, portal_url=portal_url)

                # determines the file container path in the zip archive
                zip_path = policy.getZipFilePath(
                                container_path=container_path,
                                content_id=content_id,
                                field_path=field_relative_path,
                                file_name=filename,
                                )

                # verifying duplicated fields
                zip_file_name = filename
                i = 1


                # determines the file_name
                if not zip_archive_mapping.get(zip_path):
                    zip_archive_mapping[zip_path] = list()

                while zip_file_name in zip_archive_mapping.get(zip_path):
                    ''' searching for an unused filename in this directory '''
                    zip_file_name = ".".join(tuple(filename.split(".")[:-1])) + "_" + str(i)\
                                            + "." + filename.split(".")[-1]
                    i += 1
                zip_archive_mapping[zip_path].append(zip_file_name)

                # adds the file to the zip
                zip_file_path = os.path.join(zip_path,
                                        zip_file_name)
                zip_file_path = zipNameEncode(zip_file_path, charset, self.zipCharset)
                zip.writestr(zip_file_path, retriever.fileBody())

        zip.close()
        return path


    security.declarePublic('download')
    def download(self, folder_path='',
                REQUEST=None,
                RESPONSE=None,
                with_policy=None,
                registerPath=True,
                contentBrains = None):
        """Download all the stuff"""

        portal_url = getToolByName(self, 'portal_url')

        if REQUEST is None:
            REQUEST = self.REQUEST
            RESPONSE = REQUEST.RESPONSE

        if not registerPath:
            innerStructurePolicy = PolicyRegistry.getPolicy("flat_inner_zip_structure")
        elif with_policy is None:
            innerStructurePolicy = PolicyRegistry.getPolicy(self.innerStructurePolicy)
        else:
            innerStructurePolicy = PolicyRegistry.getPolicy(with_policy)

        root = self.restrictedTraverse(folder_path)

        root_path = portal_url.getRelativeContentURL(root)

        if contentBrains is None:
            contentBrains = self.contentBrains(root)

        zip_path = self.createTemporaryZipFileFromBrains(contentBrains,
                                                         policy=innerStructurePolicy,
                                                         root_path=root_path)

        # Returning the resulting zip file
        RESPONSE.setHeader('content-type', 'application/zip')
        RESPONSE.setHeader('content-disposition',
                           'attachment; filename="%s"' % self.zipFileName(root))
        RESPONSE.setHeader('content-length', str(os.stat(zip_path)[6]))

        # If using the filestream_iterator, it wouldn't be possible to delete the out_filename later
        # So... emulating ZPublisher.Iterators.filestream_iterator
        fp = open(zip_path, 'rb')
        while True:
            data = fp.read(RESPONSE_BLOCK_SIZE)
            if data:
                RESPONSE.write(data)
            else:
                break
        fp.close()
        os.remove(zip_path)
        return

    def getRegistry(self):
        return PolicyRegistry

InitializeClass(PloneFilesZipTool)

##
# Utilities
##

def ploneWalk(top, topdown=True):
    """Kind of os.path.walk for Plone content"""

    contents = top.getFolderListingFolderContents()
    dirs = []
    atomics = []
    for content in contents:
        if isFolderish(content):
            dirs.append(content)
        else:
            atomics.append(content)
    if topdown:
        yield top, dirs, atomics
    for content in dirs:
        for x in ploneWalk(content, topdown):
            yield x
    if not topdown:
        yield top, dirs, atomics


def isFolderish(content):
    """Can we walk in this content (recursively) ?"""
    if INonStructuralFolder is not None:
        # Plone 2.1 and up
        if INonStructuralFolder.isImplementedBy(content):
            return False
    return bool(getattr(aq_base(content), 'isPrincipiaFolderish', False))


def zipNameEncode(path, plone_charset, zip_charset):
    if not type(path) is types.UnicodeType:
        path = path.decode(plone_charset, 'replace')
    path = path.encode(zip_charset, 'replace')
    path = path.replace('?', '-')
    return path


