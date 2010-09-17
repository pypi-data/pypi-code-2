from bigdoorkit.resources.base import BDResource

class Currency(BDResource):
    endpoint = "currency"

    def __init__(self, **kw):
        self.currency_type_id = kw.get('currency_type_id', None)
        self.currency_type_description = kw.get('currency_type_description', None)
        self.currency_type_title = kw.get('currency_type_title', None)
        self.exchange_rate = kw.get('exchange_rate', None)
        self.relative_weight = kw.get('relative_weight', None)
        super(Currency, self).__init__(**kw)
