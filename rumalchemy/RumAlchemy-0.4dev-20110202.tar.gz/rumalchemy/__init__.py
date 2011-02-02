from rumalchemy.repository import SARepository, SARepositoryFactory
from rumalchemy.fieldfactory import SAFieldFactory
from sqlalchemy.orm.attributes import InstrumentedAttribute
# Register jsonify rules
import rumalchemy.json
# Register SAQuery
import rumalchemy.query
# Register extensions to CRUDController
import rumalchemy.controller

from rumpolicy import Policy
def _pass_to_real_resource(self, obj, action, attr, user):
    obj=obj.parententity.class_
    return self.has_permission(obj, action, attr, user)
# Policy.register(_pass_to_real_resource, obj=InstrumentedAttribute, nested=True)



