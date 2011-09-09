from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from my315ok.portlet.rollitems import RollPortletMessageFactory as _
from collective.portlet.pixviewer import PixviewerPortletMessageFactory as _a

roll_dire_unit=[
('up','up direction',_(u'roll up')),
('down','down direction',_(u'roll down')),
('left','left direction',_(u'roll left')),
('right','right direction',_(u'roll right')),
  ]
roll_dire_terms = [
    SimpleTerm(value, token, title) for value, token, title in roll_dire_unit
]


class RollDirectionVocabulary(object):
    
    """ Ad Unit sizes """

    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary(roll_dire_terms)


RollDirectionVocabularyFactory = RollDirectionVocabulary()

image_size=[
('thumb','thumb image',_a(u'thumb image')),
('mini','mini image',_a(u'mini image')),
('preview','preview image',_a(u'preview image')),
('large','large image',_a(u'large image')),
  ]
image_size_terms = [
    SimpleTerm(value, token, title) for value, token, title in image_size
]


class ImageSizeVocabulary(object):
    """ Ad Unit sizes """

    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary(image_size_terms)


ImageSizeVocabularyFactory = ImageSizeVocabulary()
