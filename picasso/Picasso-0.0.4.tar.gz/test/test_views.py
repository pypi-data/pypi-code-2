import time
from picasso import *

def hello(req, name=None):
  req["flash"]["notice"] = "You have logged in."
  return "greetings/hello", {"name": name, "elephant": "layout"}

def bye(req):
  return "%s<br>%s" % (
    req["flash"].get("notice", "--"),
    req["flash"].get("notice", "--"))

routes = setup_routes(
  GET("/", hello),
  GET("/hello/:name", hello),
  GET("/bye", bye),
  GET('/{url:.*}', "Not Found"))

app = setup_app(routes,
  {"views": {"template_dir": "views"}})
pump.adapters.serve_with_paste(app)