import yaml
import copy
import os
import sys
import pkg_resources

def get_gunicorn_cmd(site_config, bin_dir=''):
    gconfig = copy.copy(site_config['gunicorn'])

    # Default to using a unix socket for nginx->gunicorn
    gconfig['bind'] = gconfig.get('bind', 
                                  'unix:/tmp/%s.sock' % site_config['site'])
    
    # Default to using the site name in the procname
    gconfig['name'] = gconfig.get('name', site_config['site'])

    debug = gconfig.pop('debug', None)
    options = ' '.join(['--%s %s' % (x, y) for x, y in gconfig.iteritems()])
    if debug:
        options += ' --debug'
    gconfig['options'] = options
    gconfig['bin_dir'] = bin_dir
    gconfig.update(site_config)
    cmd = 'gunicorn %(options)s %(wsgi_app)s' % gconfig
    if bin_dir:
        cmd = '%s/%s' % (bin_dir, cmd)
    return cmd

def get_site_root(start_dir):
    testfile = os.path.join(start_dir, 'site.yaml')
    if os.path.isfile(testfile):
        return start_dir
    else:
        parent_dir = os.path.split(start_dir)[0]
        if parent_dir != start_dir:
            return get_site_root(parent_dir)
        else:
            return None

def get_role_list(local_root):
    """Return a list of the role names defined by yaml roles/*.yaml"""
    return [file[:-5] for file in os.listdir(os.path.join(local_root, 'roles')) if file.endswith('.yaml')]

def get_role_config(role):
    role_file = '%s/roles/%s.yaml' % (get_site_root(os.getcwd()), role)
    config =  yaml.safe_load(open(role_file, 'r').read())
    return config
    #TODO: support pulling role info from a web page

def get_site_config(site_root):
    """Parses and returns site.yaml"""
    site_config_file = os.path.join(site_root, 'site.yaml')
    config = yaml.safe_load(open(site_config_file, 'r').read())
    return config

def get_blame(site_root):
    """Parses and returns blame.yaml in deployed site"""
    blame_file = os.path.join(site_root, 'blame.yaml')
    blame = yaml.safe_load(open(blame_file, 'r').read())
    return blame

def get_config(site_root, role=None):
    """Returns merged site and role config.
    Falls back to blame.yaml if no role given.
    Falls back to just site.yaml if no role given and no blame file found"""
    if role is None:
        try:
            return get_blame(site_root)[1]['config']
        except IOError:
            return get_site_config(site_root)
    else:
        config = get_site_config(site_root)
        config.update(get_role_config(role))
        return config

def get_template_path(template, site_root=None):
    """
    Returns path of template from site cfg_templates dir, if found there, else
    returns template path from silk's cfg_templates dir.
    """
    if site_root:
        localpath=os.path.join(site_root, 'cfg_templates', template)
        if os.path.isfile(localpath):
            return localpath
    pkgpath=pkg_resources.resource_filename('silk', 'cfg_templates/%s' % template)
    if os.path.isfile(pkgpath):
        return pkgpath
    else:
        raise Exception("Template not found: %s" % template)

def get_rendered_template(template_name, context):
    """
    Returns text of named template, with keyword substitutions pulled from
    'context'
    """
    template_path = get_template_path(template_name)
    txt = open(template_path, 'r').read()
    return txt % context

def get_role():
    try:
        #if '-R rolename' found in sys.argv, use that
        return sys.argv[sys.argv.index('-R')+1]
    except:
        #role not found in sys.argv, try env var
        #return None if no role there either
        return os.environ.get('SILK_ROLE', None)

def get_pip_cmd(site_config):
    pypi = site_config.get('pypi', 'http://pypi.python.org/simple/')
    return 'pip install -i %s' % pypi
