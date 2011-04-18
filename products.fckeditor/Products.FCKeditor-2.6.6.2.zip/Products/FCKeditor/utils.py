# -*- coding: utf-8 -*-
"""
$Id: utils.py,v 2.0 2006/01/17 22:22:13 jean-mat@ingeniweb.com Exp $
"""
__author__  = 'jean-mat Grimaldi & Gilles Lenfant - Ingeniweb'
__docformat__ = 'restructuredtext'


# Python imports
import unicodedata
import string
from StringIO import StringIO
import re
import urlparse
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot

# PloneExFile 3.x support

try:
    # Note this should be useless with PloneExFile 4
    from Products.PloneExFile import ATContentType
    HAS_PEF3 = True
    del ATContentType
except ImportError, e:
    HAS_PEF3 = False

if HAS_PEF3:
    from Products.PloneExFile.ExFile import PloneExFile

# PloneArticle 3.x support

try:
    from Products.PloneArticle.PloneArticle import PloneArticle
    HAS_PA3 = True
except ImportError, e:
    HAS_PA3 = False

security = ClassSecurityInfo()

# Make fckAbsUrl importable TTW
security.declarePublic('fckAbsUrl')
def fckAbsUrl(obj_url, portal_url, server_url, text):
    """
    Find real absolute url for href and img
    """
    # obj_url = self.absolute_url()
    html = text
    portal_path = portal_url.replace(server_url,'')

    # Method to replace src and href link by new one
    def replace_locale_url(match):
        """Compute local url
        """
        url = str(match.group('url'))
        attribute =  str(match.group('attribute'))
        if match.group('protocol') is not None:
            url = '%s%s' % (match.group('protocol'), url)

        elif not ('resolveuid' in url.lower() or url.startswith('\x23')):
            try:
                url=urlparse.urljoin (obj_url, url)
            except:
                pass

        url = url.replace(portal_url, portal_path)

        return '%s="%s"' % (attribute,url)
        #return match.group(0)

    abs_url = re.compile('(?P<attribute>href|src)\s*=\s*([\'\"])(?P<protocol>(ht|f)tps?)?(?P<url>[^\"\']*)\\2', re.IGNORECASE)
    html = abs_url.sub(replace_locale_url, html)

    return html

security.declarePublic('getFCKBrowserRoot')
def getFCKBrowserRoot(obj):
    """
    return the first parent navigation root
    """
    root = aq_inner(obj)
    while not INavigationRoot.providedBy(root) :
        root = root.aq_parent
    return root



# Make fckCreateValidZopeId importable TTW
security.declarePublic('fckCreateValidZopeId')
def fckCreateValidZopeId(s):
    """
    Return a valid Zope id from the given string
    """
    id = s.decode('utf-8')
    id = unicodedata.normalize('NFKD', id)
    id = id.encode('ascii', 'ignore')

    # remove invalid ascii chars for ids
    new_id = ''
    for a in id:
        if a in string.digits or a in string.lowercase or a in string.uppercase or a=='.' or a==' ' or a=='-' or a=='_':
            new_id += a
    new_id = new_id.replace(' ','-')
    new_id = new_id.replace('_','-')
    new_id = re.sub("-+","-", new_id)
    new_id = new_id.strip('-')
    # ids in lower case
    return new_id.lower()

# Make decodeQueryString importable TTW
from ZPublisher.HTTPRequest import HTTPRequest
security.declarePublic('decodeQueryString')
def decodeQueryString(QueryString):
    """decode *QueryString* into a dictionary, as ZPublisher would do"""
    r= HTTPRequest(None,
                   {'QUERY_STRING' : QueryString,
                    'SERVER_URL' : '',
                  },
                   None,1)
    r.processInputs()
    return r.form

# Make fckDefaultToolbar importable TTW
security.declarePublic('fckDefaultToolbar')
def fckDefaultToolbar():
    """
    Return a string for default toolbar Custom configuration
    """
    toolbar = """[
 ['Source','DocProps','-','Save','Preview','-','Templates'],
 ['Cut','Copy','Paste','PasteText','PasteWord','-','Print','rtSpellCheck'],
 ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
 ['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
 ['OrderedList','UnorderedList','-','Outdent','Indent'],
 ['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
 ['Link','Unlink','Anchor'],
 ['Image','imgmapPopup','Flash','flvPlayer','Table','Rule','SpecialChar','UniversalKey','PageBreak','Smiley'],
 ['Form','Checkbox','Radio','TextField','Textarea','Select','Button','ImageButton','HiddenField'],
 '/',
 ['Style','FontFormat','FontName','FontSize'],
 ['TextColor','BGColor'],
 ['FitWindow','-','About']
]"""

    return toolbar

# Make fckDefaultToolbar importable TTW
security.declarePublic('fckDefaultToolbar')
def fckDefaultMenuStyles():
    """
    Return a string for default Styles Menu
    """
    styles = '''
<Style name="Discreet text" element="span">
  <Attribute name="class" value="discreet" />
</Style>
<Style name="Image on Left" element="img">
  <Attribute name="class" value="image-left" />
</Style>
<Style name="Image on Right" element="img">
  <Attribute name="class" value="image-right" />
</Style>
<Style name="Image on Top" element="img">
  <Attribute name="class" value="image-inline" />
</Style>
<Style name="Listing table" element="table">
  <Attribute name="class" value="listing" />
</Style>
<Style name="Even row" element="tr">
  <Attribute name="class" value="even" />
</Style>
<Style name="Odd row" element="tr">
  <Attribute name="class" value="odd" />
</Style>
<Style name="Even block" element="div">
  <Attribute name="class" value="even" />
</Style>
<Style name="Odd block" element="div">
  <Attribute name="class" value="odd" />
</Style>
<Style name="Link Plain" element="a">
  <Attribute name="class" value="link-plain" />
</Style>
<Style name="Red Ruler" element="hr">
  <Attribute name="style" value="color: #ff0000; width:1px;" />
</Style>'''

    return styles

# Make fckDefaultKeystrokes importable TTW
security.declarePublic('fckDefaultKeystrokes')
def fckDefaultKeystrokes():
    """
    Return a string for default keystrokes behavior
    """
    keystrokes = """ [
    [ CTRL + 65 /*A*/, true ],
    [ CTRL + 67 /*C*/, true ],
    [ CTRL + 70 /*F*/, true ],
    [ CTRL + 83 /*S*/, true ],
    [ CTRL + 88 /*X*/, true ],
    [ CTRL + 86 /*V*/, 'Paste' ],
    [ SHIFT + 45 /*INS*/, 'Paste' ],
    [ CTRL + 90 /*Z*/, 'Undo' ],
    [ CTRL + 89 /*Y*/, 'Redo' ],
    [ CTRL + SHIFT + 90 /*Z*/, 'Redo' ],
    [ CTRL + 76 /*L*/, 'Link' ],
    [ CTRL + 66 /*B*/, 'Bold' ],
    [ CTRL + 73 /*I*/, 'Italic' ],
    [ CTRL + 85 /*U*/, 'Underline' ],
    [ CTRL + SHIFT + 83 /*S*/, 'Save' ],
    [ CTRL + ALT + 13 /*ENTER*/, 'FitWindow' ],
    [ CTRL + 9 /*TAB*/, 'Source' ]
]"""

    return keystrokes

# encodeString used by fck browser python scripts
from types import UnicodeType

security.declarePublic('encodeString')
def encodeString(s, encodeFrom, encodeTo) :
    """ encode a string from a encoding to another"""
    if type(s) is UnicodeType :
        return s.encode(encodeTo)
    elif encodeFrom.lower() == encodeTo.lower() :
        return s
    else:
        return unicode(s, encodeFrom).encode(encodeTo)


# Configlet validation helpers

_validsize_rx = re.compile(r'^\d+$|^\d+px$|^\d+%$')

def isValidSize(value):
    """
    Validates a size expressed as:
    * empty string (default)
    * integer value
    * integer value + 'px'
    * integer value + '%'
    @return: True if valid size
    """

    if value.strip() == '':
        return True
    mo = _validsize_rx.match(value)
    if mo is None:
        return False
    return True


def isValidStylesheet(context, name):
    """
    Validates the stylesheet name
    empty string is valid (using default)
    @return: True if valid object
    """

    if name.strip() == '':
        return True
    # Finds object with such name
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    css = getattr(portal, name, None)
    return css is not None

def isValidPath(portal, path):
    """
    Validates a path from the portal
    @param portal: Plone site
    @param path: '/xxx/yyy'
    @return: True if path is valid
    """
    if path.strip() == '':
        return True
    if not path.startswith('/'):
        return False
    try:
        # TODO: Check if we have a browsable folderish
        o = portal.restrictedTraverse(path[1:])
        return True
    except (KeyError, AttributeError), e:
        return False


# Configlet helpers (Let's avoid noise in configlet template)

from Products.ATContentTypes.interfaces import IFileContent, IImageContent

def listFileLikeTypes(portal):
    """
    All type info with File interface
    @return: see listTypesForInterface below
    """

    # Like ATFile
    flt = listTypesForInterface(portal, IFileContent)

    # PloneExFile 3.x support
    if HAS_PEF3:
        # We shall check for allowed PloneExFile and suclasses
        archetype_tool = getToolByName(portal, 'archetype_tool')
        portal_types = getToolByName(portal, 'portal_types')
        utranslate = portal.utranslate
        all_types = archetype_tool.listRegisteredTypes(inProject=True)
        all_types = [tipe['portal_type'] for tipe in all_types
                     if issubclass(tipe['klass'], PloneExFile)]
        #removed some types can be allowed in some context
        #all_types = [tipe for tipe in all_types
        #             if getattr(portal_types, tipe).globalAllow()]
        flt.extend([infoDictForType(tipe, portal_types, utranslate) for tipe in all_types if hasattr(portal_types, tipe)])
    return flt


def listImageLikeTypes(portal):
    """
    All type info with Image interface
    @param portal: Plone site
    @return: see listTypesForInterface below
    """

    return listTypesForInterface(portal, IImageContent)

from Products.Archetypes.interfaces.base import IBaseFolder
def listFolderLikeTypes(portal):
    """
    All type info with Folder interface
    @param portal: Plone site
    @return: see listTypesForInterface below
    """

    return listTypesForInterface(portal, IBaseFolder)



def listPloneArticleLikeTypes(portal):
    """
    All type info like PloneArticle
    @param portal: Plone site
    @return: see listTypesForInterface below
    """

    if HAS_PA3:
        archetype_tool = getToolByName(portal, 'archetype_tool')
        portal_types = getToolByName(portal, 'portal_types')
        utranslate = portal.utranslate
        all_types = archetype_tool.listRegisteredTypes(inProject=True)
        all_types = [tipe['portal_type'] for tipe in all_types
                     if issubclass(tipe['klass'], PloneArticle)]
        #removed some types can be allowed in some context
        #all_types = [tipe for tipe in all_types
        #             if getattr(portal_types, tipe).globalAllow()]
        return [infoDictForType(tipe, portal_types, utranslate) for tipe in all_types if hasattr(portal_types, tipe)]
    else:
        return []


def listTypesForInterface(portal, interface):
    """
    List of portal types that have File interface
    @param portal: plone site
    @param interface: Zope 2 inteface
    @return: [{'portal_type': xx, 'type_ui_info': UI type info}, ...]
    """

    archetype_tool = getToolByName(portal, 'archetype_tool')
    portal_types = getToolByName(portal, 'portal_types')
    utranslate = portal.utranslate

    # all_types = [{'name': xx, 'package': xx, 'portal_type': xx, 'module': xx,
    #               'meta_type': xx, 'klass': xx, ...
    all_types = archetype_tool.listRegisteredTypes()
    # Keep the ones that are file like
    all_types = set([tipe['portal_type'] for tipe in all_types
                    if interface.implementedBy(tipe['klass'])])
    # Keep allowed ones
    # removed some types can be allowed in some context
    # all_types = [tipe for tipe in all_types
    #             if getattr(portal_types, tipe).globalAllow()]
    return [infoDictForType(tipe, portal_types, utranslate) for tipe in all_types if hasattr(portal_types, tipe)]


def infoDictForType(ptype, portal_types, utranslate):
    """
    UI type infos
    @param ptype: a portal type name
    @param portal_types: the portal_types tool
    @param utranslate: the translation func
    @return: {'portal_type': xxx, 'type_ui_info': UI type info}
    """

    type_info = getattr(portal_types, ptype)
    title = type_info.Title()
    product = type_info.product
    type_ui_info = ("%s (portal type: %s, product: %s)" %
                    (utranslate(title, default=title), ptype, product))
    return {
        'portal_type': ptype,
        'type_ui_info': type_ui_info
        }

def listWorkflowStates(portal):
    """
    Provides all workflow states
    @return: [{'name': workflow_state, 'ui_name': friendly name}, ...]
    """

    portal_workflow = getToolByName(portal, 'portal_workflow')
    utranslate = portal.utranslate

    states = {
        # name: [translated name, workflow id, ...]
        }
    labels ={}

    for workflow in portal_workflow.objectValues():
        workflow_id = workflow.getId()
        for state_id in workflow.states.objectIds():
            if states.has_key(state_id):
                states[state_id].append(workflow_id)
            else:
                states[state_id] = [utranslate(state_id, default=state_id), workflow_id]
        # /for state_id
    # /for workflow
    state_ids = states.keys()
    state_ids.sort()
    # too long workflow list (grufspaces workflows as example ...)
    # in select input labels break the page
    for si in state_ids :
       cropLabel = labels[si] = ", ".join(states[si][1:])
       if len(cropLabel)>60:
           cropLabel = '%s ...' %cropLabel[:60]
       labels[si]=  cropLabel
    return [{'name': si,
             'ui_name': "%s (%s)" % (states[si][0],
                                    labels[si])
             }
             for si in state_ids]



def listPortalRoles(portal):
    """
    Provides all role names
    @return: [{'name', role name}, 'ui_name': friendly name}, ...]
    """

    utranslate = portal.utranslate
    return [{'name': r,
             'ui_name': "%s (%s)" % (utranslate(r, default=r), r)}
            for r in portal.validRoles()]
