import datetime

from zope.app.form.browser.widget import SimpleInputWidget, renderElement
from zope.app.form.interfaces import ConversionError
from zope.app.i18n import ZopeMessageFactory as _



class DropDownDateWidget(SimpleInputWidget):

    _missing = None

    day   = [str(i+1).zfill(2) for i in range(31)]
    month = [str(i+1).zfill(2) for i in range(12)]
    year  = [str(i+1900) for i in range(130)]

    elements = [[day,'day'],[month,'month'],[year,'year']]

    def __call__(self, *args, **kw):
        html = ''
        data = self._getFormValue()
        if data is None or data == self._data_marker:
            data = datetime.date.today()
        # day
        contents = self.renderItemsWithValues(self.elements[0][0], data.day)
        name = self.name+'.'+self.elements[0][1]
        html += renderElement('select',
                              name=name,
                              id=name,
                              contents=contents,
                              cssClass='dayField')
        html += '\n'
        # month
        contents = self.renderItemsWithValues(self.elements[1][0],data.month)
        name = self.name+'.'+self.elements[1][1]
        html += renderElement('select',
                              name=name,
                              id=name,
                              contents=contents,
                              cssClass='monthField')
        html += '\n'
        # year
        contents = self.renderItemsWithValues(self.elements[2][0],data.year)
        name = self.name+'.'+self.elements[2][1]
        html += renderElement('select',
                              name=name,
                              id=name,
                              contents=contents,
                              cssClass='yearField')
        html += '\n'
        return renderElement('div',contents=html,cssClass='dropDownDateWidget')


    def renderItemsWithValues(self, values, selected=None):
        """ Render all values from a dropdown """
        html = ''
        for value in values:
            if selected==int(value):
                html += renderElement('option',
                                      value=value,
                                      selected='selected',
                                      contents=value)
            else:
                html += renderElement('option',
                                      value=value,
                                      contents=value)
        return html


    def hasInput(self):
        prefix = self.name + '.'
        requestForm = self.request.form
        return prefix + self.elements[0][1] in requestForm and \
               prefix + self.elements[1][1] in requestForm and \
               prefix + self.elements[2][1] in requestForm


    def _getFormInput(self):
        prefix = self.name + '.'
        year = int(self.request.form.get(prefix+self.elements[2][1],None))
        month = int(self.request.form.get(prefix+self.elements[1][1],None))
        day = int(self.request.form.get(prefix+self.elements[0][1],None))
        if year and month and day:
            try:
                return datetime.date(year, month, day)
            except ValueError, v:
                raise ConversionError(_("Invalid datetime data"), v)
        else:
            return None

