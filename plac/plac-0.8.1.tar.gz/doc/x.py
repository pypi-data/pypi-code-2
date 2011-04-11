import plac
from ishelve2 import ShelveInterface
i = plac.Interpreter(ShelveInterface(configfile=None))
try:
    i.start_server(6000)
except:
    i.stop_server()
