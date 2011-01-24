import yaml
import os

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

