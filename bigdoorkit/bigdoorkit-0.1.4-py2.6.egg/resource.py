from bigdoorkit.client import Client
from bigdoorkit.exc import MissingClient, MissingParentDetails
from datetime import datetime
from types import MethodType

######
# WARNING: This code is under heavy developemnt and is not yet intended
# for public consumption.
######

__all__ = ["EndUser", "Currency", "Level", "NamedLevelCollection",
           "NamedLevel", "NamedGoodCollection", "NamedGood", "Good",
           "NamedAwardCollection", "NamedAward", "Award"]

def clean_obj_keys(data):
    """JSON returns unicode keys which cannot be passed to
    __init__ methods directly. Here we convert the keys to strings.
    """
    return dict([(str(k), v) for k, v in data.items()])

class BDResource(object):
    endpoint = None
    parent_class = None
    parent_id_attr = None

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 **kw
                ):
        self.id = id
        self.pub_title = pub_title
        self.pub_description = pub_description
        self.end_user_title = end_user_title
        self.end_user_description = end_user_description

        if isinstance(created_timestamp, (int, float)):
            created_timestamp = datetime.fromtimestamp(created_timestamp)
        self.created_timestamp = created_timestamp

        if isinstance(modified_timestamp, (int, float)):
            modified_timestamp = datetime.fromtimestamp(modified_timestamp)
        self.modified_timestamp = modified_timestamp

        # make the delete method an instance method
        self.delete = MethodType(self.__instance_delete, self, self.__class__)

        self._undefined_kw = kw

    @classmethod
    def all(cls, client):
        """Retrieves all of the available objects"""
        if cls.parent_class and not getattr(cls, cls.parent_id_attr, None):
            raise MissingParentDetails()
        endpoint = cls.endpoint
        if cls.parent_class:
            endpoint = "%s/%s/%s" % (cls.parent_class.endpoint,
                                     getattr(cls, cls.parent_id_attr),
                                     cls.endpoint)
        data = client.get(endpoint)
        return [cls(**clean_obj_keys(i)) for i in data[0]]

    @classmethod
    def get(cls, id, client):
        """Retrieves an object with the given `id`, using the `client` object
        if passed.
        """
        data = client.get("%s/%s" % (cls.endpoint, id))
        return cls(**clean_obj_keys(data[0]))

    def save(self, client):
        """Create or Update this object.

        If the object has an id, this method will try to PUT, otherwise
        the HTTP method will be POST.
        """
        if not self.id:
            client.post(self.endpoint, self.to_dict())
        else:
            data = client.put(self.endpoint, self.to_dict())
            # XXX: This is pretty dirty. We'll see how it works out.
            self = self.__class__(**data)

    def __class_delete(cls, id, client=None):
        """Deletes an object identified by `id`"""
        if client is None:
            client = get_client()
        client.delete(cls.endpoint, id)

    delete = classmethod(__class_delete)

    def __instance_delete(self, obj, client=None):
        # XXX: may need to change to self.__class__.delete(self.id, client)
        return self.__class_delete(self.id, client)

class EndUser(BDResource):
    endpoint = "end_user"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 guid=None,
                 end_user_login=None,
                 **kw):
        self.guid = guid
        self.end_user_login = end_user_login
        super(EndUser, self).__init__(id, pub_title, pub_description,
                                      end_user_title, end_user_description,
                                      created_timestamp, modified_timestamp,
                                      **kw)


class Currency(BDResource):
    endpoint = "currency"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 currency_type_id=None,
                 currency_type_description=None,
                 currency_type_title=None,
                 exchange_rate=None,
                 relative_weight=None,
                 **kw):
        self.currency_type_id = currency_type_id
        self.currency_type_description = currency_type_description
        self.currency_type_title = currency_type_title
        self.exchange_rate = exchange_rate
        self.relative_weight = relative_weight
        super(Currency, self).__init__(id, pub_title, pub_description,
                                       end_user_title, end_user_description,
                                       created_timestamp, modified_timestamp,
                                       **kw)

class Level(BDResource):
    endpoint = "level"
    parent_class = EndUser
    parent_id_attr = "end_user_login"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 end_user_login=None,
                 named_level_id=None,
                 transaction_group_id=None,
                 next_level_uri=None,
                 previous_level_uri=None,
                 **kw
                ):
        self.end_user_login = end_user_login
        self.named_level_id = named_level_id
        self.transaction_group_id = transaction_group_id
        self.next_level_uri = next_level_uri
        self.previous_level_uri = previous_level_uri
        super(Level, self).__init__(id, pub_title, pub_description,
                                    end_user_title, end_user_description,
                                    created_timestamp, modified_timestamp,
                                    **kw)


class NamedLevelCollection(BDResource):
    endpoint = "named_level_collection"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 currency_id=None,
                 **kw
                ):
        self.currency_id = currency_id
        super(NamedLevel, self).__init__(id, pub_title, pub_description,
                                         end_user_title, end_user_description,
                                         created_timestamp, modified_timestamp,
                                         **kw)

class NamedLevel(BDResource):
    endpoint = "named_level"
    parent_class = NamedLevelCollection
    parent_id_attr = "named_level_collection_id"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 named_level_collection_id=None,
                 threshold=None,
                 collection_resource_uri=None,
                 **kw
                ):
        self.named_level_collection_id = named_level_collection_id
        self.threshold = threshold
        self.collection_resource_uri = collection_resource_uri
        super(NamedLevel, self).__init__(id, pub_title, pub_description,
                                         end_user_title, end_user_description,
                                         created_timestamp, modified_timestamp,
                                         **kw)

class NamedGoodCollection(BDResource):
    endpoint = "named_good_collection"

class NamedGood(BDResource):
    endpoint = "named_good"
    parent_class = NamedGoodCollection
    parent_id_attr = "named_good_collection_id"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 named_good_collection_id=None,
                 relative_weight=None,
                 collection_resource_uri=None,
                 **kw
                ):
        self.named_good_collection_id = named_good_collection_id
        self.relative_weight = relative_weight
        self.collection_resource_uri = collection_resource_uri
        super(NamedGood, self).__init__(id, pub_title, pub_description,
                                        end_user_title, end_user_description,
                                        created_timestamp, modified_timestamp,
                                        **kw)

class Good(BDResource):
    endpoint = "good"
    parent_class = EndUser
    parent_id_attr = "reciever_end_user_login"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 sender_end_user_login=None,
                 reciever_end_user_login=None,
                 named_good_id=None,
                 end_user_message_subject=None,
                 end_user_message_body=None,
                 **kw
                ):
        self.sender_end_user_login = sender_end_user_login
        self.reciever_end_user_login = reciever_end_user_login
        self.named_good_id = named_good_id
        self.end_user_message_subject = end_user_message_subject
        self.end_user_message_body = end_user_message_body
        super(Good, self).__init__(id, pub_title, pub_description,
                                   end_user_title, end_user_description,
                                   created_timestamp, modified_timestamp,
                                   **kw)

class NamedAwardCollection(BDResource):
    endpoint = "named_award_collection"

class NamedAward(BDResource):
    endpoint = "named_award"
    parent_class = NamedAwardCollection
    parent_id_attr = "named_award_collection_id"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 named_award_collection_id=None,
                 relative_weight=None,
                 collection_resource_uri=None,
                 **kw
                ):
        self.named_award_collection_id = named_award_collection_id
        self.relative_weight = relative_weight
        self.collection_resource_uri = collection_resource_uri
        super(NamedAward, self).__init__(id, pub_title, pub_description,
                                         end_user_title, end_user_description,
                                         created_timestamp, modified_timestamp,
                                         **kw)

class Award(BDResource):
    endpoint = "award"
    parent_class = EndUser
    parent_id_attr = "end_user_login"

    def __init__(self,
                 id=None,
                 pub_title=None,
                 pub_description=None,
                 end_user_title=None,
                 end_user_description=None,
                 created_timestamp=None,
                 modified_timestamp=None,
                 end_user_login=None,
                 named_award_id=None,
                 **kw
                ):
        self.end_user_login = end_user_login
        self.named_award_id = named_award_id
        super(Award, self).__init__(id, pub_title, pub_description,
                                    end_user_title, end_user_description,
                                    created_timestamp, modified_timestamp,
                                    **kw)
