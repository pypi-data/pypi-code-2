import pickle

import sqlalchemy as sa

from amalgam.backends.base.columns import BaseColumns


class SqlaColumnMarker(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs


class SqlaColumns(BaseColumns):
    @staticmethod
    def String(max_length, type=sa.Unicode, **kwargs):
        return sa.Column(type(max_length), **kwargs)

    @staticmethod
    def Text(max_length=None, type=sa.UnicodeText, **kwargs):
        return sa.Column(type(max_length), **kwargs)

    @staticmethod
    def Boolean(**kwargs):
        return sa.Column(sa.Boolean, **kwargs)

    @staticmethod
    def Integer(**kwargs):
        return sa.Column(sa.Integer, **kwargs)

    @staticmethod
    def Float(**kwargs):
        return sa.Column(sa.Float, **kwargs)

    @staticmethod
    def Decimal(**kwargs):
        return sa.Column(sa.DECIMAL, **kwargs)

    @staticmethod
    def DateTime(**kwargs):
        return sa.Column(sa.DateTime, **kwargs)

    @staticmethod
    def Date(**kwargs):
        return sa.Column(sa.Date, **kwargs)

    @staticmethod
    def Time(**kwargs):
        return sa.Column(sa.Time, **kwargs)

    @staticmethod
    def Serialized(encode=pickle.dumps, decode=pickle.loads, **kwargs):
        class Serializer(object):
            dumps = encode
            loads = decode
        return sa.Column(sa.PickleType(pickler=Serializer()),
                         **kwargs)

    @staticmethod
    def ForeignKey(target, backref=None, relkw=None, **kwargs):
        '''Create a foreign key relationship

        :param backref:
          name of a property to be placed on a related model
        '''
        relkw = relkw or {}
        relkw['backref'] = backref
        return SqlaColumnMarker('ForeignKey', target=target,
                                relkw=relkw, **kwargs)

    @staticmethod
    def OneToOne(target, backref=None, relkw=None, **kwargs):
        '''Create a one to one foreign key relationship

        :param backref:
          name of a property to be placed on a related model
        '''
        relkw = relkw or {}
        relkw['backref'] = backref
        return SqlaColumnMarker('OneToOne', target=target,
                                relkw=relkw, **kwargs)

    @staticmethod
    def ManyToMany(target, through=None, **kwargs):
        '''Create a many to many relationship

        :param through:
          optional predefined intermediary table, which will be created
          automatically if not supplied. If supplied, should contain foreign
          keys to both ends of relationship

        :param backref:
          name of a property to be placed on a related model
        '''
        return SqlaColumnMarker('ManyToMany', target=target,
                                through=through, **kwargs)
