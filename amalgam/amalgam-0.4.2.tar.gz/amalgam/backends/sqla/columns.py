import pickle

import sqlalchemy as sa

from amalgam.backends.base.columns import BaseColumns


class SqlaColumnMarker(object):
    def __init__(self, markername, **kwargs):
        self.name = markername
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
    def Serialized(encode=None, decode=None, **kwargs):
        '''Create a column for serialized data

        :param encode:
          Encoder of data to serialized format
        :param decode:
          Decoder of data from serialized format

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
        '''
        if not encode and not decode:
            return sa.Column(sa.PickleType(), **kwargs)
        if not encode or not decode:
            raise ValueError("Both 'encode' and 'decode' should be specified")
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
        :param relkw:
          keyword arguments for :py:func:`sqlalchemy.orm.relationship`
        :param name='%(name)s_id':
          name of column
        :param type='sqlalchemy.Integer()':
          column type
        :param lazy='select':
          specifies how related items should be loaded. *Not* replicated to
          backref. See more in help of :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
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
        :param relkw:
          keyword arguments for :py:func:`sqlalchemy.orm.relationship`
        :param name='%(name)s_id':
          name of column
        :param type=sqlalchemy.Integer():
          column type
        :param lazy='select':
          specifies how related items should be loaded. *Not* replicated to
          backref. See more in help of :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
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
          name of a property to be placed on a related model or a
          :py:func:`sqlalchemy.orm.backref` object itself

        :param lazy='dynamic':
          specifies how related items should be loaded. Replicated to backref if
          it was not a ready object. See more in help of
          :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:func:`sqlalchemy.orm.relationship`
        '''
        return SqlaColumnMarker('ManyToMany', target=target,
                                through=through, **kwargs)
