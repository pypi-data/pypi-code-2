from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Date, Datetime)
from cubicweb.schema import WorkflowableEntityType


class School(EntityType):
    """an (high) school"""
    name        = String(required=True, fulltextindexed=True, maxsize=128)
    address     = String(maxsize=512)
    description = String(fulltextindexed=True)

    phone     = SubjectRelation('PhoneNumber', composite='subject')
    use_email = SubjectRelation('EmailAddress', composite='subject')


class Application(WorkflowableEntityType):
    date = Datetime(default='TODAY', required=True)
    for_person = SubjectRelation('Person', cardinality='1*', composite='object')


class comments(RelationDefinition):
    subject = 'Comment'
    object = 'Person', 'Task', 'Event'
    cardinality = '1*'
    composite = 'object'

class tags(RelationDefinition):
    subject = 'Tag'
    object = ('Person', 'Application')


class birthday(RelationDefinition):
    subject = 'Person'
    object = 'Date'

class concerned_by(RelationDefinition):
    subject = 'Person'
    object = 'File'

class has_studied_in(RelationDefinition):
    """used to indicate an estabishment where a person has been studying"""
    # XXX promotion?
    subject = 'Person'
    object = 'School'


class interested_in(RelationDefinition):
    subject = ('Person', 'CWUser')
    object = 'Event'


class todo_by(RelationDefinition):
    subject = 'Task'
    object = 'Person'


class topic(RelationDefinition):
    subject = 'EmailThread'
    object = 'Application'

