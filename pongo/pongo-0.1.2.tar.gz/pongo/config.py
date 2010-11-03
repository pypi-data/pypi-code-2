import ConfigParser
import pkg_resources

conf = None

def init_config(configfile=None):
    global conf
    if not configfile:
        configfile = pkg_resources.resource_filename('pongo',
            'conf/default.ini')

    conf = ConfigParser.ConfigParser()
    conf.read(configfile)

init_config()
