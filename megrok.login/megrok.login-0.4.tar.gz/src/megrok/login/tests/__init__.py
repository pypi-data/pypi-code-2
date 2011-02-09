import os.path
import megrok.login
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.abspath(os.path.join(os.path.dirname(
            megrok.login.__file__), 'ftesting.zcml'))
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
                            allow_teardown=True)
