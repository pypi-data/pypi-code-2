from bigdoorkit.resources.base import BDResource
from bigdoorkit.resources.user import EndUser

class NamedAwardCollection(BDResource):
    endpoint = "named_award_collection"

class NamedAward(BDResource):
    endpoint = "named_award"
    parent_class = NamedAwardCollection
    parent_id_attr = "named_award_collection_id"

    def __init__(self, **kw):
        self.named_award_collection_id = kw.get('named_award_collection_id', None)
        self.relative_weight = kw.get('relative_weight', None)
        self.collection_resource_uri = kw.get('collection_resource_uri', None)
        super(NamedAward, self).__init__(**kw)

class Award(BDResource):
    endpoint = "award"
    parent_class = EndUser
    parent_id_attr = "end_user_login"

    def __init__(self, **kw):
        self.end_user_login = kw.get('end_user_login', None)
        self.named_award_id = kw.get('named_award_id', None)
        super(Award, self).__init__(**kw)
