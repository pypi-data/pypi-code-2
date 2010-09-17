from bigdoorkit.resources.base import BDResource
from bigdoorkit.resources.user import EndUser

class NamedLevelCollection(BDResource):
    endpoint = "named_level_collection"

    def __init__(self, **kw):
        self.currency_id = kw.get('currency_id', None)
        super(NamedLevelCollection, self).__init__(**kw)

class NamedLevel(BDResource):
    endpoint = "named_level"
    parent_class = NamedLevelCollection
    parent_id_attr = "named_level_collection_id"

    def __init__(self, **kw):
        self.named_level_collection_id = kw.get('named_level_collection_id', None)
        self.threshold = kw.get('threshold', None)
        self.collection_resource_uri = kw.get('collection_resource_uri', None)
        super(NamedLevel, self).__init__(**kw)

class Level(BDResource):
    endpoint = "level"
    parent_class = EndUser
    parent_id_attr = "end_user_login"

    def __init__(self, **kw):
        self.end_user_login = kw.get('end_user_login', None)
        self.named_level_id = kw.get('named_level_id', None)
        self.transaction_group_id = kw.get('transaction_group_id', None)
        self.next_level_uri = kw.get('next_level_uri', None)
        self.previous_level_uri = kw.get('previous_level_uri', None)
        super(Level, self).__init__(**kw)
