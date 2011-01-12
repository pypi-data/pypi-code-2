import re

# Expression for variable subsitution in labels and hints
VAREXP = re.compile('\$\{[^\}]+\}')


class BaseRenderer:


    def __init__(self, **kwargs):

        """ Initialize renderer, given global options """

        self.opts = {}
        self.opts.update(kwargs)
        self._registry = {}


    def registerType(self, renderableType, renderer):

        self._registry[renderableType] = renderer


    def getRendererForType(self, renderableType):

        return self._registry.get(renderableType, None)


    def getType(self, renderable):

        """ Return the renderable's type (or class) """

        if hasattr(renderable, 'type'):

            return renderable.type

        return renderable.__class__.__name__


    def createFormatMap(self, form, renderable, **extras):

        """ Create a dict out of the renderable's properties """

        fmtmap = renderable.__dict__.copy()
        fmtmap.update(extras)


        def replaceVars(match):

            try:
                var = match.group()[2:-1]
                renderable = form.view.getRenderableByBind(var)
                return renderable.lexVal(form.data[var])
            except:
                return match.group()

        # process labels and hints
        if fmtmap.has_key('label'):
            fmtmap['label'] = VAREXP.sub(replaceVars, fmtmap['label'])
        if fmtmap.has_key('hint'):
            fmtmap['hint'] = VAREXP.sub(replaceVars, fmtmap['hint'])
  
        # defaults
        extra_classes = {'relevant':True, 'required': False, 'readonly': False}

        # Let's see whether we got properties here...
        try:
            # Requiredness
            if form.model.isRequired(renderable.bind, form.data):
                extra_classes["required"] = True

            # Relevance
            if not form.model.isRelevant(renderable.bind, form.data):
                extra_classes["relevant"] = False

            # Read only
            if form.model.isReadonly(renderable.bind, form.data):
                extra_classes["readonly"] = True
            
        except:
            pass

        if fmtmap.has_key("extra_classes"):
            fmtmap['extra_classes'] = " ".join([fmtmap['extra_classes']] + [key for key in extra_classes.keys() if extra_classes[key]])
        else:
            fmtmap['extra_classes'] = " ".join([key for key in extra_classes.keys() if extra_classes[key]])

        fmtmap['type'] = self.getType(renderable)

        return fmtmap
