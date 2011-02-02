#import grok
import grokcore.component
import zope.schema
import sqlalchemy.types
from zope.schema.interfaces import IField
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IInterface

#def Fields(model):
#    return grok.Fields(schema_from_model(model))

def schema_from_model(model):
    table = model.__table__
    bases = (Interface,)
    attrs = {}
    for i, column in enumerate(table.columns):
        if len(column.foreign_keys) or column.primary_key:
            continue
        field = IField(column.type)
        field.__name__ = str(column.name)
        field.title = unicode(column.name)
        field.required = not column.nullable
        attrs[column.name] = field
        field.order = i
       
    return InterfaceClass(name=model.__table__.name,
                          bases=bases,
                          attrs=attrs,
                          __doc__='Generated from metadata')

@grokcore.component.adapter(sqlalchemy.types.String)
@grokcore.component.implementer(IField)
def field_from_sa_string(s):
    return zope.schema.TextLine(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Text)
@grokcore.component.implementer(IField)
def field_from_sa_text(s):
    return zope.schema.Text(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Integer)
@grokcore.component.implementer(IField)
def field_from_sa_integer(i):
    return zope.schema.Int(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Float)
@grokcore.component.implementer(IField)
def field_from_sa_float(i):
    return zope.schema.Float(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.DateTime)
@grokcore.component.implementer(IField)
def field_from_sa_datetime(i):
    return zope.schema.Datetime(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Date)
@grokcore.component.implementer(IField)
def field_from_sa_date(i):
    return zope.schema.Date(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Time)
@grokcore.component.implementer(IField)
def field_from_sa_time(i):
    return zope.schema.Time(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Interval)
@grokcore.component.implementer(IField)
def field_from_sa_interval(i):
    return zope.schema.Timedelta(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Boolean)
@grokcore.component.implementer(IField)
def field_from_sa_boolean(i):
    return zope.schema.Bool(__name__ = u'__dummy__',
                title = u'__dummy__')

@grokcore.component.adapter(sqlalchemy.types.Binary)
@grokcore.component.implementer(IField)
def field_from_sa_binary(i):
    return zope.schema.Bytes(__name__ = u'__dummy__',
                title = u'__dummy__')
