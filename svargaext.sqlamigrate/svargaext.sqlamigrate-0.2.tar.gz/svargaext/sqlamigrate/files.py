import os
from migrate.versioning.version import Version, str_to_filename

def create_script(repo, description, content):
    '''Create migration script'''
    versions = repo.versions

    ver = versions.latest + 1
    extra = str_to_filename(description)

    if extra:
        if extra == '_':
            extra = ''
        elif not extra.startswith('_'):
            extra = '_%s' % extra

    filename = '%03d%s.py' % (ver, extra)
    filepath = versions._version_path(filename)

    if os.path.exists(filepath):
        raise Exception('Script already exists: %s' % filepath)
    else:
        f = file(filepath, 'w')
        f.write(content)
        f.close()

    versions.versions[ver] = Version(ver, versions.path, [filename])

    print 'Created version %s' % ver

def read_template(name):
    from svargaext.sqlamigrate import templates
    source = os.path.join(os.path.dirname(templates.__file__), name)

    f = file(source, 'r')
    content = f.read()
    f.close()

    return content

