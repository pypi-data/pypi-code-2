import logging

from Products.Archetypes.Widget import RichWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError
from Products.CMFCore.utils import getToolByName

from htmllaundry import utils
from htmllaundry import cleaners

log = logging.getLogger('slc.cleanwordpastedtext/utils.py')

def clean_word_text(text):
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = sanitize(text)
    # Make another iteration, because in some cases, an embedded comment remains.
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = sanitize(text)
    return text


def update_object_history(context, comment):
    REQUEST = context.REQUEST
    pr = getToolByName(context, 'portal_repository')
    if pr.isVersionable(context):
        # only create a new version if at_edit would not create one anyway
        if not pr.supportsPolicy(context, 'at_edit_autoversion') or \
                REQUEST.get('cmfeditions_save_new_version', None):
            try:
                context.portal_repository.save(obj=context, comment=comment)
            except FileTooLargeToVersionError:
                putils = getToolByName(context, 'plone_utils')
                putils.addPortalMessage(
                    _("Versioning for this file has been disabled because it is too large"), 
                    type="warn")
        return 'success'


def get_unicode_text(text):
    for encoding in ['utf-8', 'utf-16', 'cp1252']:
        try:
            return unicode(text, encoding)
        except UnicodeDecodeError:
            pass


def get_rich_text_fields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]


DocumentCleaner = cleaners.LaundryCleaner(
            page_structure = False,
            remove_unknown_tags = False,
            allow_tags = [ "blockquote", "a", "img", "em", "p", "strong",
                        "h1", "h2", "h3", "h4", "h5", "h6", 
                        "ul", "ol", "li", "sub", "sup",
                        "abbr", "acronym", "dl", "dt", "dd", "cite",
                        "dft", "br", "table", "tr", "td", "th", "thead",
                        "tbody", "tfoot" ],
            safe_attrs_only = True,
            add_nofollow = True,
            scripts = False,
            javascript = False,
            comments = False,
            style = False,
            links = False, 
            meta = False,
            processing_instructions = False,
            frames = False,
            annoying_tags = False
            )
                

def sanitize(input, cleaner=DocumentCleaner):
    return utils.sanitize(input, cleaner)


