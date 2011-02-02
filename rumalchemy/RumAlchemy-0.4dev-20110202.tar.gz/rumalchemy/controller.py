import logging
from rum.controller import CRUDController
import transaction
from sqlalchemy import exc

log = logging.getLogger(__name__)

#
# Extends CRUDController with exception handlers specific to SQLAlchemy
# exceptions.
#

handle_exception = CRUDController.handle_exception.im_func

def _decode(exception, encoding='utf8'):
    return unicode(str(exception), encoding, 'replace')

@handle_exception.before((CRUDController, exc.SQLAlchemyError))
def _set_response_status(self, exception, routes):
    transaction.abort()
    self.response.status_int = 400 # Bad Request

@handle_exception.before((CRUDController, exc.SQLAlchemyError))
def _log_error(self, exception, routes):
    log.error(u"Trapped %s when %r", _decode(exception), routes)

@handle_exception.when(
    "isinstance(self, CRUDController) and "
    "isinstance(exception, exc.IntegrityError)"
    )
def _handle_integrity_error(self, exception, routes):
    self.flash(u"An integrity error ocurred: %(orig)s (%(statement)s)" %
               {'orig':_decode(exception.orig),
                'statement': _decode(exception.statement)},
               status='alert')
    try:
        handler = self.error_handlers[routes['action']]
    except KeyError:
        self.app.redirect_to(action='index', id=None, _use_next=True)
    else:
        return self.forward(handler)

@handle_exception.when((CRUDController, exc.ProgrammingError))
def _handle_programming_error(self, exception, routes):
    self.flash(u"A programming error ocurred: %(orig)s (%(statement)s)" %
               {'orig':_decode(exception.orig),
                'statement': _decode(exception.statement)},
               status='alert')
    self.app.redirect_to(action='index', id=None, _use_next=True)

@handle_exception.when((CRUDController, exc.ConcurrentModificationError))
def _handle_concurrent_modification_error(self, exception, routes):
    new = self.obj
    # Since the session has gone through a rollback we need to merge the object
    self.repository.session.add(new)
    self.repository.session.merge(new)
    return self.resolve_conflict(new)
