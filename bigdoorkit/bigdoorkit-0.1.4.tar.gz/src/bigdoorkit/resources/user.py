from bigdoorkit.resources.base import BDResource

class EndUser(BDResource):
    endpoint = "end_user"

    def __init__(self, **kw):
        self.guid = guid
        self.end_user_login = kw.get('end_user_login', None)
        super(EndUser, self).__init__(**kw)
