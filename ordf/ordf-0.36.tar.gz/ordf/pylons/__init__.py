"""
ControllerFactory
-----------------

.. autofunction:: ControllerFactory
"""

def ControllerFactory(ClassName, TemplateClass, base, handler):
    """
    Factory class for creating a controller using one of the implementations
    in L{ordf.pylons}. This function is generally internal, used by the 
    implementations themselves to define a I{FooControllerFactory} which
    will only take the I{base} and I{handler} arguments. See, for example,
    L{ordf.pylons.graph.GraphControllerFactory}.

    @param ClassName: The name of the class to be returned
    @type ClassName: string

    @param TemplateClass: The implementation of the controller
    @type TemplateClass: a bare class

    @param base: The pylons project's lib.base module
    @type base: module

    @param handler: Message handler supporting read/write operations
    @type handler: instance of L{ordf.handler.Handler}
    """
    @property
    def store(self):
        return model.store
    def render(self, *av, **kw):
        return base.render(*av, **kw)
    return type(ClassName, (TemplateClass, base.BaseController),
                { "handler": handler, "render": render,
                  "__doc__": TemplateClass.__doc__ })
