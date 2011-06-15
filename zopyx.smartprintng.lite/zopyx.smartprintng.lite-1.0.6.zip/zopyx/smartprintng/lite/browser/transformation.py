################################################################
# zopyx.smartprintng.lite
# (C) 2009,  ZOPYX Limited & Co. KG, D-72070 Tuebingen, Germany
################################################################

""" HTML transformation classes (based on BeautifulSoup) """

import os
import re
import copy
import tempfile
import urllib
import urllib2
import logging
import urlparse 
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base

from zopyx.smartprintng.lite.logger import LOG

uid_reg = re.compile('([\dA-Fa-f]{32})')
level_match = re.compile('^l\d$')
url_match = re.compile(r'^(http|https|ftp)://')

TRANSFORMATIONS = dict()

LOG = logging.getLogger('zopyx.smartprintng.lite')
_log = LOG.debug


def nodeProcessed(node):
    if node.get('processed'):
        return True


def registerTransformation(method, name=''):
    name = name or method.__name__
    TRANSFORMATIONS[name] = method

class Transformer(object):

    def __init__(self, html, destdir, context):
        self.destdir = destdir
        self.soup = BeautifulSoup(html)
        self.context = context
        self.images = self._collectImages()

    def __call__(self, transformations):
        for transform in transformations:
            method = TRANSFORMATIONS.get(transform)
            params = dict(context=self.context,
                          request=self.context.REQUEST,
                          destdir=self.destdir,
                          images=self.images)
            if method is None:
                raise ValueError('No transformation "%s" registered' % transform)

            method(self.soup, params)

    def render(self):
        return self.soup.renderContents()

    def _collectImages(self):
        """ Collect paths of all images within subtree """
        images = list()
        for brain in self.context.portal_catalog(portal_type='Image',
                                                 path='/'.join(self.context.getPhysicalPath())):
            images.append(brain.getPath())
        return images



def pathFromParent(soup, node):
    """ For a given node, walk up the hierarchy in order to find
        the first node in the hierarchy above with a 'path' attribute
    """ 

    running = True
    current = node
    while running:
        current = current.parent
        path = current.get('path')
        if path:
            return str(path)

        if current == soup.body:
            running = False

    return None

def _findAll(soup, *args, **kw):
    try:
        return soup(*args, **kw)
    except:
        LOG.error('soup.findAll(%s, %s) failed' % (args, kw), exc_info=True)
        return ()


################################################################
#
################################################################

def makeImagesLocal(soup, params):
    """ deal with internal and external image references """

    for img in soup.findAll('img'):
        # 'internal' images are marked with class="internal resource"
        # in order to prevent image fetching later on
        if 'internal-resource' in (img.get('class') or ''):
            continue

        src = img['src']
        if params['request'] and src.startswith(params['request'].BASE0) \
            and '++resource++' not in src:
            src = src.replace(params['request'].BASE0 + '/', '')

        if src.startswith('http'):
            try:
                img_data = urllib2.urlopen(str(src)).read()

            except urllib2.URLError:
                LOG.warn('No image found: %s - removed from output' % src)
                img.extract()
                continue 

            tmpname = tempfile.mktemp(dir=params['destdir'])
            file(tmpname, 'wb').write(img_data)
            img['src'] = os.path.basename(tmpname)

        else:
            # image with relative URL

            # first lookup image by direct traversal 
            img_path = urllib.unquote(str(src))
            img_obj = params['context'].restrictedTraverse(img_path, None)
            if img_obj is None:
                img_path2 = getToolByName(params['context'], 'portal_url').getPortalPath() + img_path 
                img_obj = params['context'].restrictedTraverse(img_path2, None)

            if img_obj is None and 'resolveuid' in src:
                mo = uid_reg.search(src)
                if mo:
                    uid = mo.group(0)
                    img_obj = params['context'].reference_catalog.lookupObject(uid)

            # For scaled images ('_preview', '_large' etc.) use the original
            # image always (which is stored as acquisition parent)
            if img_obj:
                has_portal_type = hasattr(aq_base(img_obj.aq_inner), 'portal_type')
                if has_portal_type and img_obj.portal_type == img_obj.aq_parent.portal_type:
                    img_obj = img_obj.aq_parent

            if img_obj is None:
                # nothing found, check the next parent node with a 'path' parameter
                # referring to the origin document
                parent_container_path = pathFromParent(soup, img)
                if parent_container_path is not None:
                    img_obj = params['context'].restrictedTraverse('%s/%s' % (parent_container_path, img_path), None)

            # still nothing found
            if img_obj is None:

                img_split = img_path.split('/')
                if img_split[-1].startswith('image_') or img_split[-1].startswith('image-'):
                    img_path = '/'.join(img_split[:-1])
                for image_path in params['images']:
                    if image_path.endswith(img_path):
                        img_obj = params['context'].restrictedTraverse(image_path, None)
                        break

            # get hold of the image in original size
            if img_obj:
                # thumbnails have an Image as aq_parent
                if img_obj.aq_parent.portal_type == 'Image':
                    img_obj = img_obj.aq_parent

            if img_obj:
                img_data = None
                for attr in ['data', '_data']:
                    try:
                        img_data = str(getattr(img_obj, attr))
                        continue
                    except AttributeError:
                        pass
                if img_data == None:
                    LOG.warn('No image found: %s - removed from output' % img_path)
                    img.extract()
                    continue

                tmpname = tempfile.mktemp(dir=params['destdir'])
                file(tmpname, 'wb').write(img_data)
                img['src'] = os.path.basename(tmpname)


                # image scaling
                try:
                    scale = img_obj.getField('pdfScale').get(img_obj)
                except AttributeError:
                    scale = 100

                # add content-info debug information
                # don't add scale as style since the outer image-container
                # has the style set
                img['scale'] = str(scale)

                # now move <img> tag into a dedicated <div>
                div = Tag(soup, 'div')
                div['class'] = 'image-container'
#                div['style'] = 'width: %d%%' % scale
                div['scale'] = str(scale)
                div.insert(0, copy.copy(img))

                # image caption
                img_description = img_obj.Description()
                img_caption = Tag(soup, 'div')
                img_caption['class'] = 'image-caption'                       

                # exclude from image enumeration
                context = params['context']
                exclude_field = img_obj.getField('excludeFromImageEnumeration')
                if exclude_field and not exclude_field.get(img_obj):
                    span = Tag(soup, 'span')
                    classes = ['image-caption-text']
                    description = img_obj.Description()
                    if description:
                        classes.append('image-caption-text-with-text')
                    else:
                        classes.append('image-caption-text-without-text')
                    span['class'] = ' ' .join(classes)
                    if description:
                        span.insert(0, NavigableString(description))
                    img_caption.insert(0, span)
                    div.append(img_caption)

                img.replaceWith(div)



            else:
                LOG.warn('No image found: %s - not removed, keeping it' % img_path)


registerTransformation(makeImagesLocal)

