# -*- coding: utf8 -*-

import csv
from StringIO import StringIO
import rum.fields as field_types
import tempfile
import os

def format(s, encoding=None):
    if s is None:
        return u''
    return unicode(s)

def to_utf8(s):
    """ to_utf8(s) converts unicode to str encoded as utf-8
    >>> to_utf8(u'ham')
    'ham'
    >>> to_utf8(u'eggs')
    'eggs'
    """

    if not isinstance(s, str):
        s=format(s)
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
        writer.writerow([to_utf8(getattr(i, f.name)) for f in fields])
    value=stream.getvalue()
    stream.close()
    #bom="".join([chr(239), chr(187), chr(191)])
    return value


def to_xls(items,fields):
    
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
        obj_data=[format(getattr(obj, f.name)) for f in fields]
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


    