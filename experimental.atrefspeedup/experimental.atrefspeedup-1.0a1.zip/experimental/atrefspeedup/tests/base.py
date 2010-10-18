from Products.PloneTestCase import ptc

from . import layer

ptc.setupPloneSite()


class ATRefSpeedupTestCase(ptc.PloneTestCase):
    """ base class for integration tests """

    layer = layer.atrefspeedup
