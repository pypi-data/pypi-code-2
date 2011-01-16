from . import parsing

def _read(filename, parser=parsing.basic_parse):
    with open(filename, 'r') as f:
        return parser(list(f))

def stat(refresh=False):
    return _read('/proc/stat')

def meminfo(refresh=False):
    return _read(
        '/proc/meminfo', 
        parsing.paren_parse)

def battery_state(refresh=False, battid=0):
    return _read(
        '/proc/acpi/battery/BAT{0}/state'.format(battid), 
        parsing.paren_parse)

