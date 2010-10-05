from yams.buildobjs import (EntityType, RelationDefinition,
                            String, Datetime, RichString)

from cubicweb.schema import WorkflowableEntityType


class Task(WorkflowableEntityType):
    """something to do"""
    title  = String(required=True, fulltextindexed=True, maxsize=64)
    description = RichString(fulltextindexed=True)

    start  = Datetime(default='TODAY')
    stop   = Datetime(default='TODAY')


class todo_by(RelationDefinition):
    subject = 'Task'
    object = 'CWUser'

class depends_on(RelationDefinition):
    subject = 'Task'
    object = 'Task'

