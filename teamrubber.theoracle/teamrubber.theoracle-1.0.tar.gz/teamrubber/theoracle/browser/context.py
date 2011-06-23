from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements

class Context(BrowserView):
    implements(ICategory)
    title = "Context"

    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request
        
    def getFieldMethods(self,field):
        method_names = ['getEditAccessor','getIndexAccessor','getAccessor','getMutator']
        
        result = {}
        for method_name in method_names:
            try:
                method = getattr(field,method_name)
                field_text = method(self.context).__name__
                result[method_name] = field_text
            except Exception, err:
                result[method_name] = None
        return result
            
    def getATFields(self):
        """ Get schema fields for AT content. """
        result = []
        try:    
            fields = self.context.Schema().fields()
        except:
            return result

        for field in fields:
            if field is not None:
                try:
                    field_methods = self.getFieldMethods(field)
                    new_field = {
                                'id': field.getName(),
                                'type':field.getType(),
                                'mode':getattr(field,'mode',None),
                                'accessor': field_methods['getAccessor'],
                                'edit_accessor': field_methods['getEditAccessor'],
                                'index_accessor': field_methods['getIndexAccessor'],                                                                
                                'mutator': field_methods['getMutator'],
                                'vocabulary': getattr(field,'vocabulary',None),
                                'ismetadata': getattr(field,'ismetadata',None),
                                'required': getattr(field,'required',None),
                                'searchable': getattr(field,'searchable',None),
                                'regfield': getattr(field,'regfield',None),
                            }
                        
                    result.append(new_field)
                except:
                    pass

        return result
