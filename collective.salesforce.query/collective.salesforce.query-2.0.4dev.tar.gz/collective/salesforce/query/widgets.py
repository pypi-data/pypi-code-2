from Products.Archetypes.atapi import InAndOutWidget


class InAndOutOrderableWidget(InAndOutWidget):
    _properties = InAndOutWidget._properties.copy()
    _properties.update({
        'macro' : "orderableinandoutwidget",
        'size' : '6',
        'helper_js': ('orderableinandout.js',),
        })
