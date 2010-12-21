from paste.script import templates

class BenriTemplate(templates.Template):
    summary = 'Default benri service on the web.'
    _template_dir = 'benri'
    egg_plugins = ['benri']

# TODO: fix for upcoming release
#class ErlangTemplate(templates.Template):
#    summary = 'Creates an Erlang project template.'
#    _template_dir = 'erlang'
#    egg_plugins = ['erlang']
