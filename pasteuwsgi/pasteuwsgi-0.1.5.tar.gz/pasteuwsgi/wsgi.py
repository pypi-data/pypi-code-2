#!/usr/bin/env python
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

ini_file = "{ini}"
fileConfig(ini_file)

application = loadapp("config:%s" % (ini_file))
