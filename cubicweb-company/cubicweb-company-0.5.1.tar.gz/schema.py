# template's specific schema
from yams.buildobjs import EntityType, SubjectRelation, String

class _Base(EntityType):
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)
    headquarters = SubjectRelation('PostalAddress', cardinality='*?', composite='subject')
    web = String(fulltextindexed=True, maxsize=128)
    phone = SubjectRelation('PhoneNumber', cardinality='*?', composite='subject')
    use_email = SubjectRelation('EmailAddress', cardinality='*+', composite='subject')

class Division(_Base):
    is_part_of = SubjectRelation('Company', cardinality='1*')

class Company(_Base):
    rncs = String(fulltextindexed=True, maxsize=32)
    subsidiary_of = SubjectRelation('Company', cardinality='?*')
