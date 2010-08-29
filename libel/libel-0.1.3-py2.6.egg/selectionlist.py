class SelectionList:

    selection = []

    def __init__(self, Set):
        try:
            self.selection = Set.__iter__ and Set
        except:
            raise TypeError('%s parameter "Set" must be an iterable!' % \
                  self.__class__.__name__)

    def append(self, Item):
        self.selection.append(Item)

    def select(self, Key, Selector):
        selection = []
        for item in self.selection:
            if type(item) == type({}):
                properties = item.get(Key)
            else:
                properties = getattr(item, Key)
            if Selector.test(properties):
                selection.append(item)
        sl = SelectionList(selection)
        return sl

    def __iter__(self):
        return self.selection.__iter__()

    def __len__(self):
        return len(self.selection)

    def __contains__(self, Value):
        return Value in self.selection

    def __getitem__(self, Key):
        return self.selection[Key]


class BaseSelector:

    parameter = None

    def __init__(self, Parameter):
        self.parameter = Parameter

    def test(self, Against):
        pass


class EQUALS(BaseSelector):
    def test(self, Against):
        if Against == self.parameter:
            return True
        return False


class IN(BaseSelector):
    def __init__(self, Parameter):
        if not hasattr(Parameter, "__iter__"):
            Parameter = [Parameter]
        BaseSelector.__init__(self, Parameter)

    def test(self, Against):
        if not hasattr(Against, "__iter__"):
            Against = [Against]
        for item in Against:
            if item in self.parameter:
                return True
        return False


class ALL(IN):
    def test(self, Against):
        if not hasattr(Against, "__iter__"):
            Against = [Against]
        all_ = []
        for parameter in self.parameter:
            if parameter not in Against:
                all_.append(False)
        return not False in all_
