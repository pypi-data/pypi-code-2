from blinker import Namespace
signals = Namespace()

#: called when guest application needs to be restarted
need_restart_app = signals.signal('need-restart-app')