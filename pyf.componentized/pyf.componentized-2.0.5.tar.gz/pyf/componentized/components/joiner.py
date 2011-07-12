from pyf.componentized.components.base import Component

class DataJoiner(Component):
    strip_bypass = True
    
    def __init__(self, config_node):
        self.config_node = config_node
    
    @property
    def component(self):
        return self.launch