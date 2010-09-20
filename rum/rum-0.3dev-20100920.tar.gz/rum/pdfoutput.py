# -*- coding: utf8 -*-

from StringIO import StringIO
import rum.fields as field_types
from rum.csvoutput import to_utf8
from xml.sax.saxutils import escape
def to_pdf(items, fields, font_size=8):
    r"""
       Gives pdf representations of ``items``
       >>> fields=[field_types.String(name="spam", label="spam"), field_types.Integer(name="eggs", label="eggs")]
       >>> class HamEggs(object): pass
       >>> o1=HamEggs()
       >>> o2=HamEggs()
       >>> o1.spam="3"
       >>> o1.eggs=3
       >>> o2.spam="seven"
       >>> o2.eggs=9
       >>> items=[o1, o2]
       >>> out=to_pdf(items, fields)
    """
    stream=StringIO()
    from reportlab.platypus import Table, LongTable
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Spacer, SimpleDocTemplate,\
        Table, TableStyle, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    headers = [f.label for f in fields]
    paragraph_style = ParagraphStyle(name='data', wordWrap='CFK', fontSize=font_size)
    def format(s, field):
        if isinstance(field, field_types.Number) or isinstance(field, field_types.Date):
            return s
        else:
            return to_paragraph(s)
    def to_paragraph(s):
        # limit sizes somehow, else I get
        # LayoutError: Flowable <Table at 169782092 5 rows x 3 cols> with cell(0,0) containing '<Paragraph at 0xa20bccc>Haftungsausschluss' too large on page 3

        return Paragraph(escape(to_utf8(s))[:800], paragraph_style)
    data=[
        [format(getattr(i, f.name), f) for f in fields]
        for i in items]
    t=LongTable([headers]+data, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), font_size),
       ('ALIGN',(0,0),(-1,-1),'LEFT'),
       ('VALIGN', (0,0),(-1,-1), 'TOP'),
       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
       
    ]))
    doc=SimpleDocTemplate(stream, pagesize=(8.5*inch, 11*inch), showBoundary=0)
    from reportlab.lib.pagesizes import A4, LETTER, landscape, portrait
    doc.pagesize = landscape(A4)
    doc.build([t])
    value=stream.getvalue()
    stream.close()
    return value
    
    