from pipestack.pipe import Pipe
from httpkit.helper.response import not_found
from bn import AttributeDict

class NotFoundPipe(Pipe):

    default_aliases = AttributeDict(errordocument='errordocument')

    def enter(self, bag):
        return not_found(bag, errordocument=self.aliases.errordocument)

