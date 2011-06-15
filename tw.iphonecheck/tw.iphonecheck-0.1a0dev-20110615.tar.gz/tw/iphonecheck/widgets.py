from tw.api import JSLink, CSSLink, js_function, Widget
from tw.jquery.ui import jquery_ui_all_js
from tw.forms import CheckBox

__all__ = ["Iphonecheck"]

# declare your static resources here

# JS dependencies can be listed at 'javascript' so they'll get included
# before
my_js = JSLink(modname=__name__,
                filename='static/js/iphone-style-checkboxes.js',
                javascript=[jquery_ui_all_js])

my_css = CSSLink(modname=__name__,
                  filename='static/css/iphone-style-checkboxes.css')

class Iphonecheck(CheckBox):

    javascript = [my_js]
    css = [my_css]

    params = {
          "duration":"Time spent during slide animation",
          "checkedLabel":"Text content of 'on' state",
          "uncheckedLabel":"Text content of 'off' state",
          "resizeHandle":"Automatically resize the handle to cover either label",
          "resizeContainer":"Automatically resize the widget to contain the labels",
          "disabledClass":"css class",
          "containerClass":"css class",
          "labelOnClass":"css class",
          "labelOffClass":"css class",
          "handleClass":"css class",
          "handleCenterClass":"css class",
          "handleRightClass":"css class",
          "dragThreshold":"Pixels that must be dragged before a click is ignored",
          }

    #default
    duration=          200
    checkedLabel=      'ON'
    uncheckedLabel=    'OFF'
    resizeHandle=      True
    resizeContainer=   True
    disabledClass=     'iPhoneCheckDisabled'
    containerClass=    'iPhoneCheckContainer'
    labelOnClass=      'iPhoneCheckLabelOn'
    labelOffClass=     'iPhoneCheckLabelOff'
    handleClass=       'iPhoneCheckHandle'
    handleCenterClass= 'iPhoneCheckHandleCenter'
    handleRightClass=  'iPhoneCheckHandleRight'
    dragThreshold=     5

    def __init__(self, id=None, parent=None, children=[], **kw):
        super(Iphonecheck, self).__init__(id, parent, children, **kw)

    def update_params(self, d):
        super(Iphonecheck, self).update_params(d)
        checkbox_param= dict(duration=d.duration,
                             checkedLabel=d.checkedLabel,
                             uncheckedLabel=d.uncheckedLabel,
                             resizeHandle=d.resizeHandle,
                             resizeContainer=d.resizeContainer,
                             disabledClass=d.disabledClass,
                             containerClass=d.containerClass,
                             labelOnClass=d.labelOnClass,
                             labelOffClass=d.labelOffClass,
                             handleClass=d.handleClass,
                             handleCenterClass=d.handleCenterClass,
                             handleRightClass=d.handleRightClass,
                             dragThreshold=d.dragThreshold,
                             )
        call = js_function('jQuery("#%s").iphoneStyle' % d.id)(checkbox_param)
        self.add_call(call)
