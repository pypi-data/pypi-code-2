from zope.component import getMultiAdapter
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.configuration import zconf

from Products.validation import V_REQUIRED
from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator

from archetypes.memberdatastorage.memberpropertyfield import MemberPropertyField


#Check if maps is available
try:
    from Products.Maps.field import LocationWidget, LocationField
    HAS_MAPS = 1
except ImportError:
    HAS_MAPS = 0


from betahaus.memberprofile import MemberProfileMessageFactory as _


IMAGE_SIZES = {'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
               }

key_list = []
for key in IMAGE_SIZES:
    readable = "%s %s" % (key, str(IMAGE_SIZES[key]))
    option = (key, readable)
    key_list.append(option)
SCHEMA_IMAGE_SIZES = atapi.DisplayList( tuple(key_list) )

validation.register(MaxSizeValidator('checkNewsImageMaxSize',
                                     maxsize=zconf.ATNewsItem.max_file_size))

BaseProfileSchema = atapi.Schema((
    #Anything using a MemberPropertyField or MemberdataStorage will be 
    #saved to that user's portal_memberdata but also to Annotation storage.
    #If the user doesn't exist, Annotation storage will be used.

    #While this looks stupid, it's needed for compatibility with the fullname field in portal_memberdata.
    MemberPropertyField('fullname',
        languageIndependent = True,
        widget = atapi.StringWidget(visible = {'view':'invisible','edit':'invisible'}
                                    ),
    ),

    MemberPropertyField('firstname',
        languageIndependent = True,
        widget = atapi.StringWidget(label = _(u'firstname_label', default = u'Firstname'),
                                    ),
    ),
    MemberPropertyField('lastname',
        languageIndependent = True,
        widget = atapi.StringWidget(label = _(u'lastname_label', default = u'Lastname'),
                                    ),
    ),

    MemberPropertyField('email',
        required = True,
        searchable = False,
        languageIndependent = True,
        widget = atapi.StringWidget(
            label= _(u'email_label', default = u'Email'),
        ),
    ),

    #Should not be changable by the user
    MemberPropertyField('login_time',
        required = False,
        searchable = False,
        languageIndependent = True,
        mode = 'r',
        visible = {'view':'invisible','edit':'invisible'}
    ),

    #Should not be changable by the user
    MemberPropertyField('last_login_time',
        required = False,
        searchable = False,
        languageIndependent = True,
        mode = 'r',
        visible = {'view':'invisible','edit':'invisible'}
    ),


    #FIXME: Add url validator
    MemberPropertyField('home_page',
        required = False,
        searchable = False,
        languageIndependent = True,
        widget = atapi.StringWidget(
            label= _(u'home_page_label', default = u'Homepage'),
        ),
    ),


))



if HAS_MAPS:
    GeoLocationMixinSchema = atapi.Schema((
            LocationField('geolocation',
                languageIndependent = 1,
                default_method="getDefaultLocation",
                validators=('isGeoLocation',),
                schemata='map',
                widget=LocationWidget(label=_(u'geolocation_label', default = u'GeoLocation'),
                                      ),
                ),
    ))
else:
    GeoLocationMixinSchema = atapi.Schema((
        #dummy
    ))
    


ImageMixinSchema = atapi.Schema((
    atapi.ImageField('image',
         required = False,
         languageIndependent = True,
         sizes = IMAGE_SIZES,
         validators = (('isNonEmptyFile', V_REQUIRED),
                       ('checkNewsImageMaxSize', V_REQUIRED)),
         widget = atapi.ImageWidget(preview_scale = 'thumb',
                                    description = _(u'image_description', default = u'Image will be scaled to several different sizes.'),
                                    label= _(u'image_label', default = u'Image'),
                                    ),
         ),
))


class BaseProfile(object):
    """Base mixin for profiles"""
    
    security = ClassSecurityInfo()
    schema = BaseProfileSchema


class GeoLocationMixin(object):
    """GeoLocationMixin for content types that need a geo location"""
    security = ClassSecurityInfo()
    schema = GeoLocationMixinSchema
    
    security.declarePublic("getDefaultLocation")
    def getDefaultLocation(self):
        config = getMultiAdapter((self, self.REQUEST), name="maps_configuration")
        return config.default_location

    security.declarePublic("getMarkerIconVocab")
    def getMarkerIconVocab(self):
        config = getMultiAdapter((self, self.REQUEST), name="maps_configuration")
        marker_icons = config.marker_icons
        result = atapi.DisplayList()
        for icon in marker_icons:
            result.add(icon['name'], icon['name'])
        return result


class ImageMixin(object):
    """Mixin for anything that has a field called image that is an image."""
    security = ClassSecurityInfo()
    schema = ImageMixinSchema
    
    security.declarePublic('tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)