from yams.buildobjs import EntityType, SubjectRelation, String

try:
    from yams.buildobjs import RichString
    from yams.reader import context
    defined_types = context.defined
except ImportError:
    from cubicweb.schema import RichString

from cubicweb.schema import RQLConstraint

_ = unicode

class Person(EntityType):
    """a physical person"""
    surname   = String(required=True, fulltextindexed=True, indexed=True, maxsize=64)
    firstname = String(fulltextindexed=True, maxsize=64)
    civility  = String(required=True, internationalizable=True,
                       vocabulary=(_('Mr'), _('Ms'), _('Mrs')),
                       default='Mr')

    description        = RichString(fulltextindexed=True)

    if 'PhoneNumber' in defined_types: # from addressbook package
        phone           = SubjectRelation('PhoneNumber', composite='subject')
    if 'PostalAddress' in defined_types:
        postal_address  = SubjectRelation('PostalAddress', composite='subject')
    if 'IMAddress' in defined_types:
        im_address  = SubjectRelation('IMAddress', composite='subject')

    use_email     = SubjectRelation('EmailAddress', cardinality='*1', composite='subject')
    # allowing an email to be the primary email of multiple persons is necessary for
    # test at least :-/
    primary_email = SubjectRelation('EmailAddress', cardinality='??',
                                    constraints= [RQLConstraint('S use_email O')])


