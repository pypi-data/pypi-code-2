import copy

from zopeskel.plone import BasicZope
from zopeskel.base import get_var
from zopeskel.base import EXPERT, EASY
from zopeskel.vars import StringVar
from zopeskel import abstract_buildout

class NiteoWeb(BasicZope):
    _template_dir = 'templates/niteoweb'
    summary = "A Plone Boutique project"
    help = """"""
    category = "Plone Development"
    required_templates = ['basic_namespace']
    use_cheetah = True
    vars = copy.deepcopy(BasicZope.vars)

    # override default values for default questions
    get_var(vars, 'namespace_package').default = 'boutique'
    get_var(vars, 'package').default = 'ebar'
    get_var(vars, 'version').default = '0.1'
    get_var(vars, 'version').modes = (EXPERT)
    get_var(vars, 'description').default = 'Plone Boutique commercial project for eBar.si'
    get_var(vars, 'author').default = 'Plone Boutique Ltd.'
    get_var(vars, 'author_email').default = 'info@ploneboutique.com'
    get_var(vars, 'keywords').default = 'Python Zope Plone'

    # remove url question as it's ambigious
    vars.remove(get_var(vars, 'url'))
    
    # remove long_description question as we don't need it
    vars.remove(get_var(vars, 'long_description'))
    
    # add buildout-related questions
    vars.extend(
           [ abstract_buildout.VAR_PLONEVER,
        ]
    )
    get_var(vars, 'plone_version').default = '4.0'
    get_var(vars, 'plone_version').modes = (EXPERT)
    
    # add custom questions
    vars.append(
        StringVar(
            'xdv_version',
            title='collective.xdv version',
            description='Version of collective.xdv that you would like to use in your project.',
            modes=(EXPERT),
            default='1.0rc9',
            help="""
This value will be used to bind collective.xdv to an exact version to ensure repeatabily of your buildouts.
If you do not want to use collective.xdv in your project, leave this value blank (''). 
"""
        )
        )

    vars.append(
        StringVar(
            'hostname',
            title='Server Hostname',
            description='Domain on which this project will run on.',
            modes=(EASY, EXPERT),
            default='ebar.si',
            help=""""""
        )
        )

    vars.append(
        StringVar(
            'server_ip',
            title='IP',
            description='IP of production server. Leave default if you don\'t have one yet',
            modes=(EASY, EXPERT),
            default='87.65.43.21',
            help="""
If you have already created a Rackspace Cloud server instance, enter here it's IP address.
            """
        )
        )

    vars.append(
        StringVar(
            'temp_root_pass',
            title='Temporary root password',
            description='Temporary password for root user on production server. Leave default if you don\'t have one yet',
            modes=(EASY, EXPERT),
            default='root_password_here',
            help="""
If you have already created a Rackspace Cloud server instance, enter here its root password.
This password will only be used in the first steps of deployment and disabled immediately after.
            """
        )
        )

    vars.append(
        StringVar(
            'administrators',
            title='Administrators',
            description='Usernames of administrators that will have access to your production server, separated with commas.',
            modes=(EASY, EXPERT),
            default='bob,jane',
            help="""
This value will be used to create maintenance users that will have access to your production server.
Separate usernames with commas: 'bob,jane'
"""
        )
        )

    vars.append(
        StringVar(
            'headquarters_hostname',
            title='Headquarters Hostname',
            description='Domain on which your Headquarters server is running.',
            modes=(EASY, EXPERT),
            default='ploneboutique.com',
            help="""
Domain on which your Headquarters server is running that hosts maintenance tools along with your
main corporate website - such as Sphinx docs, Munin system monitor, etc.
            """
        )
        )

    vars.append(
        StringVar(
            'headquarters_ip',
            title='Headquarters IP',
            description='IP on which your Headquarters server is listening.',
            modes=(EASY, EXPERT),
            default='12.34.56.78',
            help="""
IP on which your main server is listening for requests from tools such as Munin system monitor, etc.
            """
        )
        )        
        
    vars.append(
        StringVar(
            'office_ip',
            title='Office IP',
            description='Your office IP that you use daily and can VPN to',
            modes=(EASY, EXPERT),
            default='12.34.56.78',
            help="""
            SSHing to this server will only be allowed from this IP. Make sure you have can VPN to this IP.
            """
        )
        )        