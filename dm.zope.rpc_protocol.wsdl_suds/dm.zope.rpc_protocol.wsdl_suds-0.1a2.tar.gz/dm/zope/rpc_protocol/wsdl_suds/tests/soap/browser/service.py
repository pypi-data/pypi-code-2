# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
from dm.zope.rpc.tests.example.browser.service import Service

class Service(Service):
  """extend the example service such that we can test result marshalling."""

  def now_and_today_dict(self):
    """return now and today as structure."""
    now, today = self.now_and_today()
    return dict(now=now, today=today)
