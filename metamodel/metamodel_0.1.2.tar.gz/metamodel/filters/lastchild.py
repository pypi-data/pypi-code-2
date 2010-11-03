from ..basemodel import SubscribableModel
from ..filters import Filter
from ..properties import Property

class LastChildsFilter(Filter):
    name = Property(str,"filter")
    query = Property(str,"")
    number = Property(int,5)
    recursive = Property(bool,False)
    model = Property(SubscribableModel)
    operations = {
         "is": lambda obj,prop,pattern: getattr(obj,prop) == pattern,
         "=": lambda obj,prop,pattern: getattr(obj,prop) == pattern,
         "==": lambda obj,prop,pattern: getattr(obj,prop) == pattern,
         "has": lambda obj,prop,pattern: pattern in str(getattr(obj,prop)),
        }


    def __init__(self,*args,**kwargs):
        self._prevmodel = None
        self._operation = None
        model = None
        if "model" in kwargs:
            model = kwargs.pop("model")
        Filter.__init__(self,*args,**kwargs)
        if model:
            self.model = model

    def setProperty(self, name, value):
        SubscribableModel.setProperty(self, name, value)
        if name == "model":
            self.set_model(value)
        if name in ["recursive","query","number"]:
            if self._prevmodel:
                self.set_model(self._prevmodel)

    def do_query(self,model,operation,propname,value,toadd):
        if (not model == self) and hasattr(model,propname) and self.operations[operation](model,propname,value):
            toadd.add(model)
            if len(toadd) == self.number:
                return toadd
        if self.recursive:
            childs = list(model.getChildren())
            childs.reverse()
            for subchild in childs:
                self.do_query(subchild, operation, propname, value, toadd)
                if len(toadd) == self.number:
                    return toadd
        return toadd

    def checkroot(self,model):
        toadd = set()
        children = list(model.getChildren())
        children.reverse()
        for child in children:
            self.do_query(child, self._operation, self._propname, self._value, toadd)
            if len(toadd) == self.number:
                return toadd
        return toadd

    def checkchild(self, child, toadd=set()):
        self.do_query(child, self._operation, self._propname, self._value, toadd)
        for child in toadd:
            self.addChildMax(child)

    def addchild(self, child):
        if self._operation:
            self.checkchild(child)
        else:
            self.addChildMax(child)

    def addChildMax(self,child):
        self.addChild(child)
        children = self.getChildren()
        if len(children) > self.number:
            self.delChild(children[0])

    def set_model(self,model):
        if self._prevmodel:
            self._prevmodel.unsubscribe(self)
            # clear
            children = list(self.getChildren())
            children.reverse()
            for child in children:
                self.delChild(child)
        if not model:
            return
        # re-fill
        self._prevmodel = model
        model.subscribe(self)
        if self.query and len(self.query.strip().split()) == 3:
            op = self.query.strip().split()
            self._operation = op[1]
            if not self._operation in self.operations:
                self._operation = None
                return
            self._propname = op[0]
            self._value = op[2]
            toadd = self.checkroot(model)
            self.process_toadd(toadd)
        else:
            children = list(model.getChildren())
            children.reverse()
            toadd = set()
            for subchild in children:
                toadd.add(subchild)
                if len(toadd) == self.number:
                    self.process_toadd(toadd)
                    return

    def process_toadd(self,toadd):
        toadd = list(toadd)
        toadd.reverse()
        for child in toadd:
            self.addChild(child)
           
    builtby = ["DataSource"]
    

