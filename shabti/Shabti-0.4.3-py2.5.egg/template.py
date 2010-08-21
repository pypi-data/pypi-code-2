from paste.script import templates
from tempita import paste_script_template_renderer

class Template(templates.Template):
    """Override template class so we can use shabti_* vars in templates
    """
    def pre(self, command, output_dir, vars):
        templates = []
        for tmpl_name in command.options.templates:
            command.extend_templates(templates, tmpl_name)
        templates = [t.name for e, t in templates]
        for entry in command.all_entry_points():
            if entry.name.startswith('shabti_'):
                vars[entry.name] = entry.name in templates
        if vars['shabti_auth_couchdb'] or vars['shabti_couchdbkit'] or vars['shabti_auth_rdfalchemy']:
            vars['elixir'] = False
        else:
            vars['elixir'] = True

class ShabtiTemplate(Template):
    egg_plugins = [ 'Shabti', 'Elixir']
    required_templates = ['pylons']
    _template_dir = 'templates/default'
    summary = 'Pylons + Elixir template'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthTemplate(Template):
    required_templates = ['shabti']
    _template_dir = 'templates/auth'
    summary = 'Shabti + simple authentication'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthXpTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_xp'
    summary = 'Shabti + row-level authentication (experimental)'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthCouchdbTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_couchdb'
    summary = 'Shabti auth using CouchDB'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiRDFAlchemyTemplate(Template):
    required_templates = ['pylons']
    _template_dir = 'templates/rdfalchemy'
    summary = 'Pylons + RDFAlchemy template'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthRepozeWhoTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_repozewho'
    summary = 'Shabti auth using repoze.who'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthRepozeWhatTemplate(Template):
    required_templates = ['shabti_auth_repozewho']
    _template_dir = 'templates/auth_repozewhat'
    summary = 'Shabti auth using repoze.what'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthRepozePylonsTemplate(Template):
    required_templates = ['shabti_auth_repozewhat']
    _template_dir = 'templates/auth_repozepylons'
    summary = 'auth + auth using repoze.what and repoze.who'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthRDFAlchemyTemplate(Template):
    required_templates = ['shabti']
    _template_dir = 'templates/auth_rdfalchemy'
    summary = "Shabti auth'n'auth using RDFAlchemy"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiMicroSiteTemplate(Template):
    required_templates = ['pylons']
    _template_dir = 'templates/microsite'
    summary = 'Pylons + auth + tw + templates + css'
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiSemWebTemplate(Template):
    required_templates = ['shabti_auth_rdfalchemy']
    _template_dir = 'templates/semweb'
    summary = "Shabti Semantic Web starter kit"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiQuickWikiTemplate(Template):
    required_templates = ['shabti']
    _template_dir = 'templates/quickwiki'
    summary = "Shabti *quick* QuickWiki"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiBlogTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/blog'
    summary = "Shabti blog"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiPyBlosxomTemplate(Template):
    required_templates = ['shabti']
    _template_dir = 'templates/pyblosxom'
    summary = "Shabti pyblosxom"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiMoinMoinTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/moinmoin'
    summary = "Shabti moinmoin"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiFormAlchemyTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/formalchemy'
    summary = "Shabti FormAlchemy example"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiCouchdbkitTemplate(Template):
    required_templates = ['shabti_auth', 'shabti_auth_repozewhat', 'shabti_formalchemy']
    _template_dir = 'templates/couchdbkit'
    summary = "Shabti couchdbkit/FormAlchemy example"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiAuthplusTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/authplus'
    summary = "Shabti auth'n'auth bundle"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiHumanoidTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/humanoid'
    summary = "Shabti vanilla SQLA auth'n'auth FA admin bundle"
    template_renderer = staticmethod(paste_script_template_renderer)


class ShabtiShenuTemplate(Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/shenu'
    summary = "Shenu blogging app"
    template_renderer = staticmethod(paste_script_template_renderer)

