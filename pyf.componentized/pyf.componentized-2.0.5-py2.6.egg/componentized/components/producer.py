from pyf.componentized.components.base import Component
class Producer(Component):
    
    def __init__(self, config_node, name):
        self.name = name
        self.config_node = config_node