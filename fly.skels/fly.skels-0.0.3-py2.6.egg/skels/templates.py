from fly.skels.base import var
from fly.skels.base import get_var
from fly.skels.base import BaseTemplate


class Mini(BaseTemplate):
    _template_dir = 'tmpl/package'
    summary = "A namespaced package"
    use_cheetah = True

    vars = [
        var('namespace_package', 'Namespace package (like fly)', 
             default='fly'), 
        var('package', 'The package contained namespace package (like example)',
            default='example'),
        var('version', 'Version', default='0.1.0'),
        var('description', 'One-line description of the package'),
        var('author', 'Author name',default='Young King'),
        var('author_email', 'Author email',default='youngking@flyzen.com'),
        var('keywords', 'Space-separated keywords/tags'),
        var('url', 'URL of homepage',default='http://www.flyzen.com'),
        var('license_name', 'License name', default='BSD'),
        var('zip_safe', 'True/False: if the package can be distributed '
            'as a .zip file', default=False),
        ]

    def check_vars(self, vars, command):
        if not command.options.no_interactive and \
           not hasattr(command, '_deleted_once'):
            del vars['package']
            command._deleted_once = True
        return super(Mini, self).check_vars(vars, command)

