import time, string, random
from coils.core import CoilsException

class CollectionAssignmentFlyWeight(object):
    __slots__ = ('revision', 'description', 'object_id', '__entityName__', 'sort_key')

    def __init__(self, data, ctx=None):
        self.revision    = None  # TODO: Implement preloading the revision
        self.description = None  # TODO: Implement preloading the description
        self.sort_key    = None
        if(isinstance(data, dict)):
            self.object_id = int(data.get('assignedObjectId', data.get('objectId')))
            self.fill_from_dict(ctx, data)
        elif (isinstance(data, int)):
            self.object_id = data
            self.fill_from_id(ctx)
        elif (isinstance(data, basestring)):
            if (data.isdigit()):
                self.object_id = int(data)
                self.fill_from_id(ctx)
            else:
                raise CoilsException('Non-numeric string presented as objectId.')
        elif (hasattr(data, 'object_id')):
            # We are assuming this is an entity or an appropriate fly-weight
            self.object_id = data.object_id
            self.fill_from_entity(ctx, data)
        else:
            raise CoilsException('Unable to comprehend assignment entity of type "{0}"'.format(type(data)))

    def fill_from_id(self, ctx):
        self.__entityName__ = ctx.type_manager.get_type(self.object_id)

    def fill_from_entity(self, ctx, entity):
        self.__entityName__ = entity.__entityName__

    def fill_from_dict(self, ctx, value):
        if ('entityName' in value):
            self.__entityName__ = value['entityName']
        if ('targetEntityName' in value):
            self.__entityName__ = value['entityName']
        else:
            self.__entityName__ = ctx.type_manager.get_type(self.object_id)
        self.sort_key = value.get('sortKey', value.get('sort_key', None))

    def __repr__(self):
        return '<CollectionAssignmentFlyweight assignedId={0} entityName="{1}">'.format(self.object_id, self.__entityName__)

class AttachmentCommand(object):

    def generate_attachment_id(self):
        return '{0}-{1}-{2}-{3}@{4}'.\
            format(''.join(random.sample(string.letters+string.digits,10)),
                   self._ctx.account_id,
                   ''.join(random.sample(string.letters+string.digits,10)),
                   int(time.time() * 1000000),
                   self._ctx.cluster_id)

    def attachment_text_path(self, attachment):
        return 'attachments/{0}/{1}/{2}'.format(attachment.uuid[0:1].upper(),
                                                attachment.uuid[2:3].upper(),
                                                attachment.uuid)