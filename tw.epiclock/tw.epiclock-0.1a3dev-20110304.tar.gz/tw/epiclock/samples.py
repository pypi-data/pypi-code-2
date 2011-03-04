"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""

from tw.epiclock import Epiclock

class DemoEpiclock(Epiclock):
    # Provide default parameters, value, etc... here
    # default = <some-default-value>
    demo_for = Epiclock
    pass
