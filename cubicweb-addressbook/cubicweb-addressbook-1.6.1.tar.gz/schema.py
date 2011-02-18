from yams.buildobjs import EntityType, String, Float

_ = unicode

class PhoneNumber(EntityType):
    number = String(fulltextindexed=True, required=True, maxsize=64)
    type = String(required=True, internationalizable=True,
                  vocabulary=((_('mobile'), _('home'), _('office'),
                               _('fax'), _('secretariat'))),
                  default=u'mobile')

class PostalAddress(EntityType):
    street  = String(fulltextindexed=True, required=True, maxsize=256)
    street2  = String(fulltextindexed=True, maxsize=256)
    postalcode = String(fulltextindexed=True, required=True, maxsize=256)
    city    = String(fulltextindexed=True, required=True, maxsize=256)
    country = String(fulltextindexed=True, maxsize=256)
    state   = String(fulltextindexed=True, maxsize=256)
    latitude = Float()
    longitude = Float()

class IMAddress(EntityType):
    im_account  = String(fulltextindexed=True, required=True, maxsize=64)
    type = String(required=True, internationalizable=True,
                  vocabulary=('jabber', 'icq', 'msn'),
                  default=u'jabber')
