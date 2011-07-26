from paste.registry import StackedObjectProxy
import transaction

app = StackedObjectProxy(name="active Rum application", default=None)

from rum.i18n import _, N_
from rum.view import ViewFactory
from rum.controller import ControllerFactory, Controller, BuiltinResource
from rum.repository import RepositoryFactory, Repository
from rum.query import QueryFactory, Query
from rum.fields import FieldFactory, rum_setattr, rum_getattr
from rum.router import RumRouter
from rum.wsgiapp import RumApp
from rum.templating import BaseRenderer

# Registers jsonify rules
from rum import json


__all__ = [
    "BuiltinResource",
    "transaction",
    "app",
    "rum_setattr",
    "rum_getattr",
    "RumApp",
    "Controller",
    "ControllerFactory",
    "Repository",
    "RepositoryFactory",
    "Query",
    "QueryFactory",
    "FieldFactory",
    "ViewFactory",
    "RumRouter",
    "BaseRenderer",
    "_",
    "N_",
    ]
