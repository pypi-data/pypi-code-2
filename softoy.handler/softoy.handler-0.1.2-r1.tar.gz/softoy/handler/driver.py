# -*- coding: utf-8 -*-
from softoy.widgets import widgets as w

class Handle(object):
    def __init__(self, **kw):
        self.driver = None
        self.form_method = kw.get('form_method','POST')    # POST or GET

    def params(self):
        return self.driver.params()


class SubmitHandle(Handle):
    def __init__(self, **kw):
        super(SubmitHandle, self).__init__(**kw)
        self.button_name = kw.get('button_name', 'b_submit')
        self.button_text = kw.get('button_text', u'보내기')
        self.element = w.Submit(name=self.button_name, value=self.button_text)
        
    def __repr__(self):
        return self.element.render()


CMII = '_cmii_'


class Driver(object):
    model = None
    widgets = []
    handles = []
    request = None
        
    def __call__(self, request):
        self.request = request
        for h in self.handles:
            h.driver = self
        return self
        
    def params(self):
        if self.request.POST:
            return self.request.POST
        else:
            return self.request.GET

    def set_handles(self):
        for h in self.handles:
            h.driver = self
            self.widgets.append(h.element)

    def delete_handles(self):
        indexes = []
        for e in self.widgets:
            if isinstance(e, w.InputButton):
                indexes.append(self.widgets.index(e) )
        indexes.sort()
        indexes.reverse()
        for i in indexes:
            h = self.widgets.pop(i)
        return self

    def form(self):
        for e in self.widgets:
            e.error = None
        self.delete_handles()
        for h in self.handles:
            self.widgets.append(h.element)
        return w.Form().multi_append(self.widgets)

    def get_model_name(self):
        return self.model_name

    def fire_event(self):
        for h in self.handles:
            if self.request.method == h.form_method and h.button_name in h.params():
                return h.driver.inst_or_editform()

    def find_handle(self):
        for h in self.handles:
            if self.request.method == h.form_method and h.button_name in h.params():
                return h

    def inst_or_editform(self):
        values, errors = self.form().validate(self.params())
        if errors:
            fm = self.form()
            fm.fill(self.params(), errors=errors)
            return fm
        else:
            field_values = {}
            for a in self.model._fields_:
                try:
                    field_values[a] = values[a]
                except KeyError:
                    pass
            inst = self.model(**field_values)
            return inst
            
    def is_model_inst(self, o):
        return isinstance(o, self.model)

    def validate(self):
        values, errors = self.form().validate(self.params())
        if errors:
            fm = self.form()
            fm.fill(self.params(), errors=errors)
            return fm
        else:
            return values

    def edit_form(self, o):
        fm = self.form()
        fm.refill(o)
        fm.listform()
        return fm


