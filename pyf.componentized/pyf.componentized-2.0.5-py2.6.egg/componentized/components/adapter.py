from pyf.componentized.components.base import Component

class BaseAdapter(Component):
    def __init__(self, config_node, name):
        self.node_name = name
        self.config_node = config_node