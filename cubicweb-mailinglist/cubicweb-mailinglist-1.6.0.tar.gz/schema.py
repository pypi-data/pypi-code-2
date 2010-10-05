from yams.buildobjs import EntityType, SubjectRelation, String
from yams.reader import context

try:
    from yams.buildobjs import RichString
except ImportError:
    from cubicweb.schema import RichString

class MailingList(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners'),
    }
    ## attributes
    name  = String(fulltextindexed=True, maxsize=64)
    mlid  = String(indexed=True, maxsize=64,
                   description=_('mailing list id specified in messages header'))
    description = RichString(fulltextindexed=True, maxsize=512)

    archive = String(maxsize=256, description=_("URL of the mailing-list's archive"))
    homepage = String(maxsize=256, description=_("URL of the mailing-list's admin page"))
    ## relations
    use_email = SubjectRelation('EmailAddress', cardinality='1?',
                                description=_('email address to use to post on the mailing-list'))


if 'Email' in context.defined:
    class sent_on(RelationType):
        """mailing list on which the email was sent"""
        subject = 'Email'
        object = 'MailingList'
