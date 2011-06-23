from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory,IDebugger
from zope.interface import implements
from zope.component import getUtility
import inspect
from teamrubber.theoracle.utils import safe_import


class Control(BrowserView):
    
    def __call__(self):
        message = ""
        action = self.request.form.get('action')
        if action is not None:
            debugger = getUtility(IDebugger)
            if action == 'add':
                line = int(self.request.form['line'])
                module = self.request.form['module']
                try:
                    mod = safe_import(module)
                    filename = inspect.getsourcefile(mod)
                except:
                    filename = None
                    
                debugger.add_break(filename,line)
                message = "Breakpoint added"
            elif action == 'remove':
                bid = self.request.form['id']
                debugger.remove_break(int(bid))
                message = "Breakpoint removed"
            elif action == "perm":
                bid = int(self.request.form['id'])
                debugger.set_temporary(bid,0)
                message = "Breakpoint set as permanent"
            elif action == "temp":
                bid = int(self.request.form['id'])
                debugger.set_temporary(bid,1)
                message = "Breakpoint set as temporary"
                
                
        return self.request.response.redirect(self.context.absolute_url() + "/the_oracle?category=breakpoints&message=" + message)



class Breakpoints(BrowserView):
    implements(ICategory)
    title = "Breakpoints"
    
    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request

    def getEnabled(self):
        return getUtility(IDebugger).is_installed()


    def getBreaks(self):
        debugger = getUtility(IDebugger)
        result = []
        i = 0
        for b in debugger.get_breaks():
            if b:
                result.append({'filename':b.file,
                               'line':b.line,
                               'id':i,
                               'temporary':b.temporary})
            i+=1
        return result
        

    def __call__(self):
        return self.index()
        


