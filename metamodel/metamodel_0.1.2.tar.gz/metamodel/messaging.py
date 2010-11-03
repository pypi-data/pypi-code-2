from metamodel import SubscribableModel, Property

class Signal(SubscribableModel):
    name = Property(str, 'a signal')

class Socket(SubscribableModel):
    name = Property(str, 'a socket')

