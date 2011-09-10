# PyMonitor is a module written by Jonas Svensson that is used to add support
# enable runtime monitoring/inspecting of an running Python application.
# http://pymonitor.sf.net

import PyMonitor.monitor as monitor
mon = monitor.MonitorServer(('127.0.0.1',8881))
mon.start()
