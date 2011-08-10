from logging import getLogger
import re
import urlparse

from DocumentTemplate.DT_Util import html_quote
from plone.app.linkintegrity.handlers import getObjectsFromLinks
from plone.app.linkintegrity.parser import extractLinks
from Products.Archetypes.exceptions import ReferenceException
from Products.Archetypes.Field import TextField, ReferenceField
from Products.CMFCore.utils import getToolByName
from Products.kupu.plone.html2captioned import decodeEntities, LINK_PATTERN

referencedRelationship = 'isReferencing'
UIDURL = re.compile(".*\\bresolveuid/([^/?#]+)")

log = getLogger('collective.updatelinksoncopy')


def handleObjectCopied(obj, event):
    """ copied event - scribble on the obj so we know later after the
    clone event who the original object was. Interestingly all objects
    in the subtree of the root object copied will get the same
    event.original, and therefore the same _v_copy_root_path will be
    available to all the objects that get the cloned event below. This
    is useful because the algorithm in
    textFieldLinkUpdaterObjectCloned is then able to deal with the
    situation where nested objects from CopyRoot that point to other
    objects - e.g. siblings in CopyRoot will also have their
    references updated."""

    obj._v_copy_root_path  = '/'.join(event.original.getPhysicalPath())
    log.info('IN OBJECT COPIED EVENT - setting obj._v_copy_root_path of ' + obj.id + ' to ' + obj._v_copy_root_path)

def handleObjectCloned(obj, event):
    """ cloned event We are luck here too, the PasteRoot is provided
    to us by event.object on all occurances of this event for the
    copy/paste of CopyRoot to PasteRoot"""

    copy_root_obj = obj.unrestrictedTraverse(obj._v_copy_root_path)
    copy_root_obj_path = '/'.join(copy_root_obj.getPhysicalPath())
    paste_root_obj = event.object
    paste_root_obj_path = '/'.join(paste_root_obj.getPhysicalPath())

    def checklink(match):
        matched = match.group(0)
        newlink = link = decodeEntities(match.group('href'))
        if UIDURL.match(link):
            linked_object = findResolveuidObject(link, obj)
            if linked_object:
                linked_object_path = '/'.join(linked_object.getPhysicalPath())
                if linked_object_path.startswith(copy_root_obj_path + '/'):
                    sub_path = linked_object_path.replace(copy_root_obj_path,'', 1)
                    newlink = find_new_link_from_resolveuid_path(sub_path, obj, link)
                    log.info('resolveuid replace ' + link + ' with ' + newlink)
        else:
            # link not a resolve uid link
            if link.startswith(copy_root_obj_path + '/'):
                # check site root relative paths only
                newlink = link.replace(copy_root_obj_path, paste_root_obj_path, 1)
                log.info('non-resolveuid replace ' + link + ' with ' + newlink)
            if link.startswith('..'):
                # relative url to possibly outside of CopyRoot
                current_obj_path = '/'.join(obj.getPhysicalPath())
                orig_obj_path = current_obj_path.replace(paste_root_obj_path, copy_root_obj_path, 1)
                # root_relative_link points to where the original link pointed to but as a root relative url
                root_relative_link = urlparse.urljoin(orig_obj_path, link)
                if not root_relative_link.startswith(copy_root_obj_path):
                    # time to update link, it was outside of CopyRoot and descendants
                    log.info('relative link ' + link + ' needs updating')
                    newlink = generate_relative_path(current_obj_path, root_relative_link)
        if newlink != link:
            prefix = match.group('prefix')
            newlink = html_quote(newlink).encode('ascii', 'xmlcharrefreplace')
            return prefix + newlink
        return matched

    reference_tool = getToolByName(obj, 'reference_catalog')
    for field in obj.Schema().fields():
        #XXX perhaps only test text/html fields?
        if isinstance(field, TextField):
            accessor = field.getEditAccessor(obj)
            data = accessor().decode('utf8')
            newdata = LINK_PATTERN.sub(checklink, data)
            if data != newdata:
                mutator = field.getMutator(obj)
                if mutator:
                    mutator(newdata.encode('utf8'), mimetype='text/html')
                    obj.reindexObject() # Need to flag update
                    modifiedArchetype(obj)
                    #event.notify(ObjectModifiedEvent(obj))
        if isinstance(field, ReferenceField):
            current_obj_path = '/'.join(obj.getPhysicalPath())
            orig_obj_path = current_obj_path.replace(paste_root_obj_path, copy_root_obj_path, 1)
            orig_obj = obj.unrestrictedTraverse(orig_obj_path)
            accessor = field.getEditAccessor(orig_obj)
            try:
                data = accessor() or []
            except Exception:
                log.info('Could not find edit accessor for ' + orig_obj.absolute_url())
                data = field.getRaw(orig_obj) or []
            if not isinstance(data, list):
                # sometimes values returned are sngle valued
                data = [data]
            uids = []
            field_name = field.getName()
            orig_obj_url = orig_obj.absolute_url()
            for UID in data:
                log.info('reference field (%s) data for %s %s' % (
                    field_name, orig_obj_url, str(data)))
                linked_object = reference_tool.lookupObject(UID)
                if not linked_object:
                    # oops
                    log.info("targeted object not found for uid: %s" % UID)
                    continue
                linked_object_path = '/'.join(linked_object.getPhysicalPath())
                log.info("found linked object " + linked_object_path)
                #if we find orig root in its path then redefine new path, find object and add reference for obj
                if linked_object_path.startswith(copy_root_obj_path + '/'):
                    log.info('need to update reference field for ' + linked_object_path)
                    copy_of_linked_object_path = linked_object_path.replace(copy_root_obj_path, paste_root_obj_path)
                    copy_of_linked_object = obj.unrestrictedTraverse(copy_of_linked_object_path)
                    uids.append(copy_of_linked_object.UID())
                    log.info('UID found for copy of linked object ' + copy_of_linked_object_path)
                else:
                    # reference to object outside of copy tree, need to add this too
                    log.info('add reference field for ' + linked_object_path)
                    uids.append(UID)
                mutator = field.getMutator(obj)
                mutator(uids)


def findResolveuidObject(src, context):
    log.info('in findResolveuidObject: looking at ' + src)
    match = UIDURL.match(src)
    if match:
        uid = match.group(1)
        reference_tool = getToolByName(context, 'reference_catalog')
        return reference_tool.lookupObject(uid)
    return None

def find_new_link_from_resolveuid_path(sub_path, obj, old_link):
    """
    find the object which is located sub_path relative to obj and use
    this to create a new resolveuid link based on the old link.

    e.g.

    old_link = 'resolveuid/12345/some/more'
    sub_path = 'ping/pong'
    pong.UID() == '6789'
    new_link == 'resolveuid/6789/some/more'
    """
    if sub_path.startswith('/'):
        sub_path = sub_path[1:]
    new_linked_obj = obj.unrestrictedTraverse(sub_path)
    new_linked_obj_uid = new_linked_obj.UID()
    new_resolve_link_part = 'resolveuid/' + new_linked_obj_uid
    new_link = UIDURL.sub(new_resolve_link_part, old_link)
    return new_link

def modifiedArchetype(obj):
    """ an archetype based object was modified """
    try:    # TODO: is this a bug or a needed workaround?
        existing = set(obj.getReferences(relationship=referencedRelationship))
    except AttributeError:
        return
    refs = set()
    for field in obj.Schema().fields():
        if isinstance(field, TextField):
            accessor = field.getAccessor(obj)
            links = extractLinks(accessor())
            refs = refs.union(getObjectsFromLinks(obj, links))
    for ref in refs.difference(existing):   # add new references and...
        try:
            obj.addReference(ref, relationship=referencedRelationship)
        except ReferenceException:
            pass
    for ref in existing.difference(refs):   # removed leftovers
        obj.deleteReference(ref, relationship=referencedRelationship)


def generate_relative_path(origin, dest):
    """
    Generate a relative url from origin to destination. Origin and destination need to be absolute paths

    >>> from collective.updatelinksoncopy.handlers import generate_relative_path
    >>> print generate_relative_path(u'/plone/Members/test_user_1_/copy_of_folder_a/folder_b/document_in_b',
    ...                              u'/plone/Members/test_user_1_/folder_z/document_in_z')
    ../../folder_z/document_in_z
    >>> print generate_relative_path(u'/plone/Members/test_user_1_/copy_of_folder_a/folder_b/document_in_b',
    ...                              u'/plone/Members/test_user_1_/folder_z/document_in_z?&x=3')
    ../../folder_z/document_in_z?&x=3
    >>> print generate_relative_path(u'/plone/Members/test_user_1_/copy_of_folder_a/folder_b/document_in_b/x/y/z',
    ...                              u'/plone/Members/test_user_1_/folder_z/document_in_z?&x=3')
    ../../../../../folder_z/document_in_z?&x=3

    """
    # if the first item is a filename, we want to get rid of it
    orig_list = origin.split('/')[:-1]
    dest_list = dest.split('/')
    #
    # find the location where the two paths start to differ.
    i = 0
    for start_seg, dest_seg in zip(orig_list, dest_list):
        if start_seg != dest_seg:
            break
        i += 1

    # now i is the point where the two paths diverge.
    # need a certain number of "os.pardir"s to work up
    # from the origin to the point of divergence.
    segments = ['..'] * (len(orig_list) - i)
    # need to add the diverging part of dest_list.
    segments += dest_list[i:]
    if len(segments) == 0:
        # if they happen to be identical paths
        # identical directories
        if dest.endswith('/'):
            return ''
        # just the filename - the last part of dest
        return dest_list[-1]
    else:
        return '/'.join(segments)
