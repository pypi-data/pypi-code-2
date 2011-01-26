import logging

from ordf.onto.lib.base import BaseController, request, response, session, c, config
from pylons.controllers.util import abort, redirect
from webhelpers.html.builder import literal

log = logging.getLogger(__name__)

class HomeController(BaseController):
    def index(self):
        c.site_title = config.get("site_title", "ORDF Python Library")
        return self.render("base.html")
