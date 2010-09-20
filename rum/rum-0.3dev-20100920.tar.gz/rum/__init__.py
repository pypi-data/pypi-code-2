from paste.registry import StackedObjectProxy
import transaction

app = StackedObjectProxy(name="active Rum application", default=None)

from rum.i18n import _, N_
from rum.view import ViewFactory
from rum.controller import ControllerFactory, Controller
from rum.repository import RepositoryFactory, Repository
from rum.query import QueryFactory, Query
from rum.fields import FieldFactory
from rum.router import RumRouter
from rum.wsgiapp import RumApp
from rum.templating import BaseRenderer

# Registers jsonify rules
from rum import json


__all__ = [
    "transaction",
    "app",
    "RumApp",
    "Controller",
    "ControllerFactory",
    "Repository",
    "RepositoryFactory",
    "Query",
    "QueryFactory",
    "FieldFactory",
    "ViewFactory",
    "RumRouter"
    "BaseRenderer",
    "_",
    "N_",
    ]
