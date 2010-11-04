from zope.interface import Interface

class IAnnotationBrowserView(Interface):
    
    def ann_keys():
        """ Returns available (not blacklisted) annotation keys """

    def ann_dict():
        """ Returns available (not blacklisted) annotation values as a dictionary.
            Too long values are stripped """

    def num_blacklisted():
        """ Returns count of blacklisted keys """
    