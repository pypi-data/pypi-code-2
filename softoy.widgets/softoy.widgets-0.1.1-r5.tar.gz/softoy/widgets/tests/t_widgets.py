# -*- coding: utf-8 -*-
from softoy.widgets import widgets as w
from formencode.validators import FancyValidator, Int, UnicodeString as Ustr

project_widgets = [
    w.Hidden(name='_id',validator=Int()),
    w.Text(name='name', label=u'프로젝트', validator=Ustr(not_empty=True)),
    w.Text(name='nickname', label=u'별명', validator=Ustr()),
    w.Text(name='due', label=u'기한', validator=Ustr()),
    w.Text(name='state', label=u'상태', validator=Ustr(not_empty=True)),
    w.TextArea(name='note', label=u'비고', style={'width':'40em', 'height':'2em'},
        validator=Ustr()),
    w.Submit(name='b_submit')
    ]


def test():
    pform = w.Form().multi_append(project_widgets)
    #print pform.literalize()

    values = dict(
        _id=None,
        name='R&E Building',
        due='2010-9-11',
        note='zzz')
    pform.fill(values)
    #print pform.literalize()

    #print pform.filled()

    pform = w.Form().multi_append(project_widgets)
    vs, es =pform.validate(values)
    #print vs
    print '@@', es

    pform.fill(vs, errors=es)
    print pform.literalize()

#test()




