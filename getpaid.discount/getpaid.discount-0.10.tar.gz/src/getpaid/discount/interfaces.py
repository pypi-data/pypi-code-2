from zope.interface import Interface

class IGetPaidDiscountLayer(Interface):
    """Marker applied to the request during traversal of sites that
       have Carousel installed
    """
