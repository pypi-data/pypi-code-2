from ConfigParser import SafeConfigParser
from prettytable import PrettyTable

def process_file(file_name):
    config_parser = SafeConfigParser()
    config_parser.read(file_name)
    versions = dict(config_parser.items('versions'))
    return versions
    
new = process_file('releases/bluebream-1.0a2.cfg')
old = process_file('releases/zope-3.4.0.cfg')

chart = PrettyTable(["Package Name", "Zope 3.4.0", "BlueBream 1.0.0"])
chart.set_field_align("Package Name", "l")
chart.set_padding_width(1)
chart.set_field_align("Zope 3.4.0", "l")
chart.set_padding_width(1)
chart.set_field_align("BlueBream 1.0.0", "l")
chart.set_padding_width(1)

data = []

for package, version in new.items():
    if package in old:
        data.append([package, old[package], version])
    else:
        data.append([package, '', version])

for row in data:
    chart.add_row(row)

chart.printt(hrules=1,sortby="Package Name")
