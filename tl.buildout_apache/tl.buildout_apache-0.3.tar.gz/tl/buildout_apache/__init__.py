# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import pkg_resources
import ConfigParser


config_file = pkg_resources.resource_stream(__name__, "defaults.cfg")
config = ConfigParser.ConfigParser()
config.readfp(config_file)
