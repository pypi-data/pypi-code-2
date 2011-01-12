from zope.interface import implements
from gw20e.forms.interfaces import IControl
from renderables import Renderable


REPR="""%(type)s %(id)s, bound to '%(bind)s':
  label: %(label)s
  hint: %(hint)s
  help: %(help)s
  alert: %(alert)s
  """

DEFAULTS = {'input':
                {"rows": 1, "cols": 20},
            'select':
                {"multiple": "", "size": "1", "format": "compact"}
            }



class Control(Renderable):

    """ Base class for controls """

    implements(IControl)

    def __init__(self, id, bind, label, hint="", help="", alert="", **props):

        Renderable.__init__(self, id, **props)

        self.bind = bind
        self.label = label
        self.hint = hint
        self.help = help
        self.alert = alert

        defaults = DEFAULTS.get(self.type, {}).copy()
        defaults.update(props)

        self._custom_props = props.keys()

        self.__dict__.update(defaults)


    def __repr__(self):

        return REPR % self.__dict__


    def processInput(self, data={}):

        """ Base implementation """

        return data.get(self.id, None)


    def lexVal(self, value):

        return value


class Input(Control):

    """ Base input """


class File(Control):
    
    """ File upload control """


class Checkbox(Control):

    """ Checkbox """


class RichText(Control):

    """ Base input """


class ColorPicker(Input):

    """ Whatever... """


class Option:

    def __init__(self, value, label):

        self.value = value
        self.label = label
        self.selected = "false"


class Select(Control):

    def __init__(self, id, bind, label, options=[], **properties):

        Control.__init__(self, id, bind, label, **properties)
        self._options = options


    @property
    def options(self):

        if self.__dict__.get("with_empty", False):

            return [Option("", "Maak een keuze")] + self._options

        return self._options


    def addOptions(self, option):

        self.options.append(option)


    def lexVal(self, value):

        if type([]) == type(value):

            res = []

            for val in value:

                res.append(self.lexVal(val))

            return res
            
        else:
            for opt in self.options:

                if opt.value == value:

                    return opt.label

        return value


class SelectAll(Select):

    """ Select including 'all' option """
