try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi


from archetypes.schemaextender.field import ExtensionField
from simplelayout.types.common import websiteMessageFactory as _

class imageAlternativeTextField(ExtensionField,atapi.StringField):
    """
    """

class showImageTitle(ExtensionField, atapi.BooleanField):
    """
    """

image_alternative_text = imageAlternativeTextField('imageAlternativeText',
                                  schemata='default',
                                  widget=atapi.StringWidget(label=_('Image Alternative Text'),
                                                      description=_('image_help_image_alternative_text'),
                                                      ),
                                  required=1
                                  )

show_image_title = showImageTitle ('showImageTitle',
                schemata='default',
                default=0,
                widget=atapi.BooleanWidget(label = _('Show image title'),
                                     description = _('image_help_show_image_title'),
                                     ),
                )

