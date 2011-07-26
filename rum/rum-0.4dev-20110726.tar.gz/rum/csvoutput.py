# -*- coding: utf8 -*-

import csv
from StringIO import StringIO
import rum.fields as field_types
from rum.fields import rum_getattr
import tempfile
import os

from rum.genericfunctions import generic

def register_field_for_csv_output(resource, field_name, suited=True):
    if isinstance(field_name, field_types.Field):
        field_name=field_name.name
    my_resource = resource

    @suitable_field_for_csv_output.when('issubclass(resource, my_resource) and field.name==field_name', prio=1000)
    def _register_field(resource, field):
        return suited
        
@generic
def suitable_field_for_csv_output(resource, field):
    '''return True if field should appear in csv outputs.
    The policy is checked from controller and not in this function.
    So this function should mostly control only not not blow up csv data
    '''
    pass

@suitable_field_for_csv_output.when('isinstance(field, field_types.RelatedField)', prio=-1)
def _handle_related_fiels(resource, field):
    return suitable_field_for_csv_output(resource, field.real_field)

@suitable_field_for_csv_output.when('isinstance(field, field_types.Collection)', prio=-1)
def _disable_collections(resource, field):
    '''
    >>> f=field_types.List('bar', other=None, remote_name=None)
    >>> suitable_field_for_csv_output(None, f)
    False
    '''
    return False


@suitable_field_for_csv_output.when()
def _default_true(resource, field):
    '''
    >>> f=field_types.Unicode('ham')
    >>> suitable_field_for_csv_output(None, f)
    True
    '''
    return True

@suitable_field_for_csv_output.when('isinstance(field, field_types.Binary)', prio=-1)
def _disable_binaries(resource, field):
    '''
    >>> f=field_types.Binary('foo')
    >>> suitable_field_for_csv_output(None, f)
    False
    
    '''
    return False

@generic
def format(value, field):
    pass

@format.when('value is None')
def _format_None(value, field):
    return u''

@format.when()
def _default_format(value, field):
    return unicode(value)
    
@format.when('isinstance(field, field_types.List) and value is not None', prio=-1)
def _format_list(value, field):
    return '\n'.join([unicode(s) for s in value])
    
def to_utf8(s, f):
    """ to_utf8(s) converts unicode to str encoded as utf-8
    >>> f=field_types.Field('ham')
    >>> to_utf8(u'ham', f)
    'ham'
    >>> to_utf8(u'eggs', f)
    'eggs'
    """

    if not isinstance(s, str):
        s=format(s, f)
        s=s.encode("utf8")
    return s

def table_headers(fields):
    return [unicode(f.label) for f in fields]
 
def to_csv(items, fields):
    r"""
       Gives csv representations of ``items``
       >>> fields=[field_types.String(name="spam", label="spam"), field_types.Integer(name="eggs", label="eggs")]
       >>> class HamEggs(object): pass
       >>> o1=HamEggs()
       >>> o2=HamEggs()
       >>> o1.spam="3"
       >>> o1.eggs=3
       >>> o2.spam="seven"
       >>> o2.eggs=9
       >>> items=[o1, o2]
       >>> to_csv(items, fields)
       'spam,eggs\r\n3,3\r\nseven,9\r\n'
    """
    stream=StringIO()
    writer=csv.writer(stream, dialect='excel')
    writer.writerow(table_headers(fields))
    for i in items:
        writer.writerow([to_utf8(rum_getattr(i, f), f) for f in fields])
    value=stream.getvalue()
    stream.close()
    #bom="".join([chr(239), chr(187), chr(191)])
    return value


def to_xls(items,fields):
    r"""
       Gives csv representations of ``items``
       >>> fields=[field_types.String(name="spam", label="spam"), field_types.Integer(name="eggs", label="eggs")]
       >>> class HamEggs(object): pass
       >>> o1=HamEggs()
       >>> o2=HamEggs()
       >>> o1.spam="3"
       >>> o1.eggs=3
       >>> o2.spam="seven"
       >>> o2.eggs=9
       >>> items=[o1, o2]
       >>> len(to_xls(items, fields))>0
       True
    """
    from xlwt import Workbook, Font, XFStyle
   
    mydoc=Workbook()
    mysheet=mydoc.add_sheet("data")
    #write headers
    header_font=Font() #make a font object
    header_font.bold=True
    header_font.underline=True
    #font needs to be style actually
    header_style = XFStyle()
    header_style.font = header_font
    
    for pos, header in enumerate(table_headers(fields)):
        mysheet.write(0,pos,header,header_style)
    for pos, obj in enumerate(items):
        obj_data=[format(rum_getattr(obj, f), f) for f in fields]
        for i, value in enumerate(obj_data):
            mysheet.write(pos+1,i,value)
    #save file
    (handle, tempfile_name)=tempfile.mkstemp(suffix='.xls')
    try:
        os.close(handle)
        mydoc.save(tempfile_name)
        out_reader =open(tempfile_name)
        res=out_reader.read()
        out_reader.close()
        return res
    finally:
        os.remove(tempfile_name)


    