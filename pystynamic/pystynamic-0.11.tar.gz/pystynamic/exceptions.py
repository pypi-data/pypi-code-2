class ResourceNotFound(Exception): pass

class TooManyTemplatesFound(Exception):
    def __init__(self, template_list):
        self.template_list = template_list
        msg = 'More than one template was found. Templates found: [{0}]'
        msg = msg.format(', '.join(template_list))
        Exception.__init__(self, msg)

class CircularDependency(Exception):
    def __init__(self, initialize_stack):
        self.initialize_stack = initialize_stack
        msg = 'A circular dependency was found while initializing resources.\n'
        msg += '  ' + ' -> '.join(initialize_stack)
        Exception.__init__(self, msg)
