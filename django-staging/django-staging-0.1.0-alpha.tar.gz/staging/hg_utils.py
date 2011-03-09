import os
import subprocess
import tempfile
import urllib2

from staging import exceptions


HG_COMMAND = 'hg'


def _get_files_from_stat(stdout, hg_type=None):
    files = []
    for line in stdout.readlines():
        line = line.strip()
        if hg_type and not line.startswith(hg_type):
            continue
        files.append(line.split(' ')[1])
    return files


def hg_init_repo(repo):
    p = subprocess.Popen([HG_COMMAND, 'init', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        return False
    return True


def hg_check_repo(repo):
    p = subprocess.Popen([HG_COMMAND, 'identify', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        return False
    return True


def hg_server_ready(port):
    url = 'http://localhost:%s/' % port
    headers = {
        "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
        "Accept-Language": "en-us,en;q=0.5",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Connection": "close",
        "User-Agent": "django-staging",
    }
    url = url.encode('utf-8')
    try:
        req = urllib2.Request(url, None, headers)
        u = urllib2.urlopen(req)
    except:
        return False
    else:
        return True


def hg_get_lost_files(repo, path):
    p = subprocess.Popen([HG_COMMAND, 'stat', '-d', path, '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return _get_files_from_stat(p.stdout)


def hg_get_removed_files(repo):
    p = subprocess.Popen([HG_COMMAND, 'stat', '-r', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return _get_files_from_stat(p.stdout)


def hg_get_added_files(repo):
    p = subprocess.Popen([HG_COMMAND, 'stat', '-a', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return _get_files_from_stat(p.stdout)


def hg_remove_files(repo, files):
    if not files:
        return
    p = subprocess.Popen([HG_COMMAND, 'remove'] + files + ['-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return True


def hg_get_new_files(repo, path):
    p = subprocess.Popen([HG_COMMAND, 'stat', '-u', path, '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return _get_files_from_stat(p.stdout)


def hg_add_files(repo, files):
    if not files:
        return
    p = subprocess.Popen([HG_COMMAND, 'add'] + files + ['-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return True


def hg_get_tip(repo):
    p = subprocess.Popen([HG_COMMAND, 'tip', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p.stdout.read()


def hg_diff(repo):
    p = subprocess.Popen([HG_COMMAND, 'diff', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p.stdout.read()


def hg_commit(repo, message):
    p = subprocess.Popen([HG_COMMAND, 'commit', '-m', message, '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p.stdout.read()


def hg_log(repo, revision=None):
    if revision:
        p = subprocess.Popen([HG_COMMAND, 'log', '-R', repo, '-r', revision, '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen([HG_COMMAND, 'log', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p.stdout.read()


def hg_files(repo, revision):
    p = subprocess.Popen([HG_COMMAND, 'log', '-R', repo, '-r', revision, '--template', "{files}\n{file_adds}\n{file_dels}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p.stdout.read()


def hg_serve(repo, port=8888):
    # Just for testing purpouses!!! Without access control!!!
    p = subprocess.Popen([HG_COMMAND, 'serve', '-d', '-R', repo, '-p', port, '--config', "'web.allow_push=*'", '--config', "'web.push_ssl=false'"])
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return p


def hg_update(repo):
    p = subprocess.Popen([HG_COMMAND, 'update', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return True


def hg_push(repo, url):
    p = subprocess.Popen([HG_COMMAND, 'push', '-R', repo, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return True


def hg_bundle(repo):
    temp_file = os.path.join(tempfile.gettempdir(), 'bundle.hg')
    p = subprocess.Popen([HG_COMMAND, 'bundle', '--all', '-R', repo, temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    fp = open(temp_file, 'rb')
    # TODO: put more logic to handle big repositories
    return fp.read()


def hg_unbundle(repo, stream):
    temp_file = os.path.join(tempfile.gettempdir(), 'bundle_to_import.hg')
    fp = open(temp_file, 'wb')
    fp.write(stream.read())
    fp.close()
    p = subprocess.Popen([HG_COMMAND, 'unbundle', '-R', repo, temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    p = subprocess.Popen([HG_COMMAND, 'update', '-R', repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise exceptions.HGException(p.stderr.read())
    return True
