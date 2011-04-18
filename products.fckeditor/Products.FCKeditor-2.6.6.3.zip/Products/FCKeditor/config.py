# Authors: Ingeniweb <support@ingeniweb.com>
#
"""
"""
import Globals
try:
    from App.Common import package_home
except ImportError:
    from Globals import package_home
try:
    from Products.CMFCore.permissions import View, ManagePortal
except ImportError: # For instances with old CMF products
    from Products.CMFCore.CMFCorePermissions import View, ManagePortal

from utils import fckDefaultToolbar,  fckDefaultKeystrokes, fckDefaultMenuStyles

GLOBALS = globals()

PROJECTNAME = "FCKeditor"
SKINS_DIR = 'skins'
PRODUCT_VERSION="2.6.6"
# Set to True if you want to try Demo types (Plone 2.5 only)
INSTALL_DEMO_TYPES = False

# these properties will be updated when reinstalling fckeditor
#(you can set it to an empty list at your own risk )
UPDATE_PROPERTIES = ['fck_custom_toolbar','keyboard_customkeystrokes']

# by default all static contents are stored one week in browser or proxies caches.
FCKHTTPCACHE_DURATION = 604800

SKIN_LAYERS = ("fckeditor","fckeditorplone")

# small fckeditor jscripts loaded in portal_javascripts

FCK_JSCRIPTS = [('fckeditor.js',
                 {'enabled' : True,
                  'cookable' : True,
                  'compression' : 'safe',
                  'cacheable' : True}),
                ('fck_plone.js',
                 {'enabled' : True,
                  'cookable' : True,
                  'compression' : 'safe',
                  'cacheable' : True}),]

FCK_KSS = [('fckeditor_plone.kss',
            {'enabled' : True,
             'cookable' : True,
             'compression' : 'safe',
             'cacheable' : True}),]

fckeditor_properties = (
    ('start_expanded', 'boolean', 1),
    ('allow_link_byuid', 'boolean', 1),
    ('allow_relative_links', 'boolean', 1),
    ('allow_latin_entities', 'boolean', 0),
    ('force_paste_as_text', 'boolean', 0),
    ('keyboard_entermode', 'string', 'p'),
    ('keyboard_shiftentermode', 'string', 'br'),
    ('keyboard_keystrokesmode', 'string', 'standard'), #could be custom
    ('keyboard_customkeystrokes', 'text', fckDefaultKeystrokes()),
    ('spellchecker', 'string', 'ieSpell'),
    ('fck_force_width', 'string', ''),
    ('fck_force_height', 'string', ''),
    ('fck_toolbar', 'string', 'PloneDefaultToolbar'),
    ('fck_custom_toolbar', 'text', fckDefaultToolbar()),
    ('allow_server_browsing', 'boolean', 1),
    ('allow_file_upload', 'boolean', 1),
    ('allow_image_upload', 'boolean', 1),
    ('allow_flash_upload', 'boolean', 1),
    ('file_portal_type', 'string', 'File'),
    ('image_portal_type', 'string', 'Image'),
    ('browse_images_portal_types', 'lines', ['Image','ATPhoto','ATImage']),
    ('flash_portal_type', 'string', 'File'),
    ('browse_flashs_portal_types', 'lines', ['File','ATFile','Flash']),
    ('folder_portal_type', 'string', 'Folder'),
    ('pa_meta_types', 'lines', ['PloneArticle','MyPloneArticleType']),
    ('rd_portal_types', 'lines', ['RichDocument', 'RichPage']),
    ('fck_area_style', 'lines', []),
    ('fck_force_path', 'boolean', 0), # force path to personal member folder
    ('fck_force_other_path', 'string', ''), # force path to other folder
    ('fck_force_other_path_method', 'string', ''), # force path with a contextual method
    ('fck_force_root', 'boolean', 0),  # force browser root to personal member folder
    ('fck_force_other_root', 'string', ''), # force root to other folder
    ('fck_force_other_root_method', 'string', ''), # force root with a contextual method
    ('fck_default_skin', 'string', 'default'),
    ('fck_menu_styles', 'text', fckDefaultMenuStyles()),
    ('fck_default_r2l', 'boolean', 0), # default edition from right to left
    ('fck_unpublished_states', 'lines', ['visible','pending','rejected', 'waitreview']), # states which need to be hidden even when user have permission view
    ('fck_unpublished_view_roles', 'lines', ['Manager','Reviewer','Owner', 'Contributor']), # roles allowed to view unpublished contents
    )

memberData_properties = (
    ('fck_skin', 'string', ''), # member can change fckeditor skin not set by default
    ('fck_path', 'string', ''), # member can choose browser opening path if path is not forced
    ('fck_root', 'string', ''), # member can choose browser root if root is not forced
    )


fckeditor_configlet = {
    'id': 'fckeditor_configlet',
    'appId': 'FCKeditor',
    'name': 'FCKeditor configuration',
    'action': 'string:$portal_url/prefs_fckeditor_form',
    'category': 'Products',
    'permission': (ManagePortal,),
    'imageUrl': 'fckPlone_icon.gif',
    }

fckeditor_member_prefs = {
    'id': 'fckeditor_member_prefs',
    'appId': 'FCKeditor',
    'name': 'FCKeditor preferences',
    'action': 'string:$portal_url/prefs_fckeditor_member',
    'condition': 'not:object/portal_membership/isAnonymousUser',
    'permission': ('View',),
    'category': 'Member',
    'imageUrl': 'fckPlone_icon.gif',
    }

# Copyright: quintagroup.com (from qPloneResolveUID product)
RUID_URL_PATTERN = 'resolveuid'
DOCUMENT_DEFAULT_OUTPUT_TYPE = "text/x-html-safe"
REQUIRED_TRANSFORM = ["fck_ruid_to_url"]
TAG_PATTERN = r'(\<(img|a|embed)[^>]*>)'
UID_PATTERN = r'[^"]*\./%s/(?P<uid>[^/"#? ]*)' %RUID_URL_PATTERN

