from django.conf import settings
from django.db.models.signals import class_prepared
from table_prefix.utils import get_table_name, models_is_prefixed


def prefix_table(sender, *args, **kwargs):
    """ connect to model's class after preparation and adjust DB table name
    """
    if models_is_prefixed(sender):
        sender._meta.db_table = get_table_name(sender._meta.db_table)
    for f in sender._meta.local_many_to_many:
        if not isinstance(f.rel.to, str):
            f.rel.to._meta.db_table = get_table_name(f.rel.to._meta.db_table)

class_prepared.connect(prefix_table)

