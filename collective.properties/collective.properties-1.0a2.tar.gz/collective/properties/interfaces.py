from zope.schema.interfaces import ITuple
from z3c.form.interfaces import ISelectWidget, IOrderedSelectWidget


class IBytesLineTuple(ITuple):
    """Tuple containing byte strings inside.
    We use separate field to attach custom data converter
    from byte string to text area widget.
    """

class ISpecialSelectWidget(ISelectWidget):
    """SelectWidget which doesn't break if there is not current value
    inside widget terms.
    Also it handles any data types correctly and inline with how
    IPropertyManager does it, so /manage_properitesForm still works.
    """

class ISpecialOrderedSelectWidget(IOrderedSelectWidget):
    """Ordered Select Widget which doesn't break if current field value contains
    items which are not within widget terms.
    Also it handles any data types correctly and inline with how
    IPropertyManager does it, so /manage_properitesForm still works.
    """
