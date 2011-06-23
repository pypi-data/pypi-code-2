from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements
from AccessControl import getSecurityManager
from types import MethodType
import inspect

def getRoles(container, name):

    value = getattr(container,name)
    default = {'roles':None,'permission':None}
    
    _noroles = object()
    roles = getattr(value, '__roles__', _noroles)
    if roles is _noroles:
        if not name or not isinstance(name, basestring):
            return default

        if type(value) is MethodType:
            container = value.im_self

        cls = getattr(container, '__class__', None)
        if cls is None:
            return default
        
        roles = getattr(cls, name+'__roles__', _noroles)
        if roles is _noroles:
            return default

        value = container

    if roles is None or isinstance(roles, (tuple,list)):
        return {'roles':roles,'permission':None}
    
    rolesForPermissionOn = getattr(roles, 'rolesForPermissionOn', None)
    if rolesForPermissionOn is not None:
        return {'roles':rolesForPermissionOn(value),'permission':roles.__name__}

    return {'roles':roles,'permission':None}



def isFunction(method):
    """ Is something functionish, because callable is a bit generic for us """
    if hasattr(method,'__class__'):
        if '<type' in repr(method.__class__):
            type_name = repr(method.__class__).split("'")[1]
            if type_name in ['function','instancemethod','builtin_function_or_method']:
                return True 
    else:
        pass
    return False

def getParameters(method):
    """ Get a pretty string of parameters """
    try:
        arg_info = inspect.getargspec(method)
    except TypeError:
        return None
    arg_names = arg_info[0]
    arg_defaults = arg_info[3]
    if arg_defaults == None:
        arg_defaults = []
    offset = len(arg_names)-len(arg_defaults)
    result = []
    for i in range(len(arg_names)):
      if i-offset >= 0:
          
        default = arg_defaults[i-offset]
        if isinstance(default,basestring):
            default = '"%s"' % str(default)
        if hasattr(default,'__name__'):
            default = default.__name__
            
        value = "%s=%s" % (str(arg_names[i]),str(default))
      else:
        value = "%s" % (str(arg_names[i]))

      if arg_names[i] == arg_info[1]:
          value = "*" + value
     
      if arg_names[i] == arg_info[2]:
          value = "**" + value
    
    
      result.append(value)
    return ', '.join(result)

class Callables(BrowserView):
    implements(ICategory)
    title = "Callables"
    
    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request

    def getRoles(self):
        sm = getSecurityManager()
        user = sm.getUser()
        return ", ".join(user.getRolesInContext(self.context))
    
    def getMethodURL(self,name):
        """ No guarantee we can trust aq """
        url = self.request.get("ACTUAL_URL","")
        split = url.rfind(self.oracle.__name__)
        if split >= 0:
            return url[:split] + name

        # Fallback to something that at least roughly resembles
        # correctness
        return name
            
    def getCallables(self):
        result = []
        user_roles = self.getRoles()
        
        if hasattr(self.context,'aq_base'):
            ob = self.context.aq_base
        else:
            ob = self.context
        
        
        for attr_name in dir(ob):
            try:
                attr = getattr(ob,attr_name)
            except AttributeError:
                attr = None
            if attr is not None and isFunction(attr):
                try:
                    roles = getRoles(ob,attr_name)
                    
                    if not roles['roles']:
                        display_roles = ""
                    else:
                        display_roles = ", ".join(roles['roles'])
                    
                    security = "Public"
                    if roles['permission'] is not None:
                        security = "Protected (%s)" % roles['permission']
                    elif roles['roles'] is not None:
                        if not roles['roles']:
                            security = "Private"
                        else:
                            security = "Explicit roles (%s)" % ", ".join(roles['roles'])
                    
                    
                    attrdata = {'name':attr_name,
                                'doc':getattr(attr,'__doc__',None),
                                'module':getattr(attr,'__module__',None),
                                'params':getParameters(attr),
                                'roles':display_roles,
                                'security':security}

                    can_call = False
                    if attrdata['doc'] is not None and attrdata['name'][0] != '_':
                        if roles['roles'] is None:
                            can_call = True
                        else:
                            for role_name in roles['roles']:
                                if role_name in user_roles:
                                       can_call = True
                    
                    attrdata['can_call'] = can_call
                    result.append(attrdata)
                    
                except Exception, e:
                    pass
        return result
        
        
        
    