"""
The html builder should be worked on..
"""
import webhelpers.html.builder

from formtags import util

class HTMLBuilder(object):
    """
    Quick implementation of a HTML builder. Builds the actual html tags
    and returns it wrapped in a literal.
    """
    @util.literal
    def input(self, attributes):
        """
        Return a HTML input element
        """
        return '<input %s>' % attributes

    @util.literal
    def textarea(self, attributes, value):
        """
        Return a HTML textarea element
        """
        value = webhelpers.html.builder.escape(value)
        return '<textarea %s>%s</textarea>' % (attributes, value)

    @util.literal
    def label(self, attributes, value):
        """
        Return a HTML label element
        """
        return '<label%s>%s</label>' % (attributes.space_string(), value)
    
    @util.literal
    def select(self, attributes, options, value):
        """
        Return a HTML select element.
        """
        data = []
        data.append('<!-- value = %s -->' % value)
        data.append('<select%s>' % attributes.space_string())
        
        # Iterate over the options and build html option tags
        for opt_value, opt_label in options:
            opt_selected = ' selected="selected"' if opt_value == value else ''
            opt_value = webhelpers.html.builder.escape(opt_value)
            opt_label = webhelpers.html.builder.escape(opt_label)
            data.append('<option value="%s"%s>%s</option>' % (opt_value,
                                                              opt_selected,
                                                              opt_label))
        data.append('</select>')
        return '\n'.join(data)        


class BaseCtrl(object):
    """
    Class to construct radion button controls. Used by FormTags.radiogroup()
    """
    def __init__(self, html_attributes, label):
        """
        Create a RadioButtonCtrl.
        """
        self._html_attributes = html_attributes
        self._label = label

    @util.literal
    def label(self, prepend='', append=''):
        """
        Return a HTML label element.
        """
        return '<label for="%s">%s%s%s</label>' % (self._html_attributes['id'],
                                                   prepend,
                                                   self._label,
                                                   append)
    
class RadioButtonCtrl(BaseCtrl):
    @util.literal
    def widget(self):
        """
        Return a HTML input element with type 'radio'.
        """
        self._html_attributes['type'] = 'radio'
        return '<input %s>' % self._html_attributes


class CheckboxCtrl(BaseCtrl):
    @util.literal
    def widget(self):
        """
        Return a HTML input element with type 'radio'.
        """
        self._html_attributes['type'] = 'checkbox'
        return '<input %s>' % self._html_attributes