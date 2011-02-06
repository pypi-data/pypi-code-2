from dm.dom.stateful import SimpleDatedObject
from dm.dom.stateful import String
from dm.dictionarywords import SYSTEM_VERSION

class System(SimpleDatedObject):
    "Kforge installation."

    version = String(
        default=SimpleDatedObject.dictionary[SYSTEM_VERSION]
    )
    mode = String(isRequired=False)

    def getLabelValue(self):
        return "%s %s %s" % (
            self.version,
            self.dateCreated,
            self.mode,
        )

