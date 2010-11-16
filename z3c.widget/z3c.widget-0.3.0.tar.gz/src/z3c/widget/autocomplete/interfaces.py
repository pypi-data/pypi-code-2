from zope import interface

class IAutoCompleteWidget(interface.Interface):

    def getSuggestions(value):

        """returns a list of suggestions for a given value"""

    def __call__():

        """renders the widget"""
