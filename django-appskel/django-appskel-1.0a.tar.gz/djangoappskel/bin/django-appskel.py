#!/usr/bin/env python

import djangoappskel
import datetime
import os
import codecs
from jinja2 import Environment, FileSystemLoader

egg = raw_input("""Name of egg (eg. django-myapp): """)
module = raw_input("""Name of module (eg. myapp): """)
readme_ext = raw_input("""Extension of README (empty for default .txt): """)
if readme_ext == '':
    readme_ext = 'txt'
description = raw_input("""Short description: """)
author = raw_input("""Author: """)
email = raw_input("""Author email: """)
url = raw_input("""App url (leave empty for repo url): """)
repo_url = None
repo_type = raw_input("""Code repo (github, bitbucket, url) or empty: """)
if repo_type in ('github', 'bitbucket'):
    repo_user = raw_input("""Repo user: """)
    repo_url = (repo_type == 'github' and 'http://github.com/%s/%s.git') or 'http://bitbucket.org/%s/%s/'
    repo = repo_url % (repo_user, egg)
else:
    repo = repo_type
rtfd = raw_input("""On Read The Docs (y/N): """)
rtfd = rtfd == 'y'
transifex = raw_input("""On Transifex (y/N): """)
transifex = transifex == 'y'
if url == '':
    url = repo
    
context = {
    'egg': egg,
    'module': module,
    'readme_ext': readme_ext,
    'description': description,
    'author': author,
    'email': email,
    'url': url,
    'repo': repo,
    'rtfd': rtfd,
    'transifex': transifex,
    'year': datetime.datetime.today().strftime('%Y')
}

for k in context:
    if isinstance(context[k], basestring):
        context[k] = context[k].decode('utf-8')

cwd = os.path.abspath(os.getcwd())
root_dir = os.path.dirname(djangoappskel.__file__)
skeldir = os.path.abspath(os.path.join(root_dir, 'skel'))
env = Environment(loader=FileSystemLoader(skeldir))

print "Skeleton at: %s" % skeldir
for dirpath, dirnames, filenames in os.walk(skeldir):
    original_dirpath = dirpath
    replaced_dirpath = os.path.join(cwd, dirpath.replace('__module__', module)[len(skeldir)+1:])
    relative_dirpath_src = dirpath[len(skeldir)+1:]
    for dirname in dirnames:
        dirname = dirname.replace('__module__', module)
        newdir = os.path.join(replaced_dirpath, dirname)
        os.mkdir(newdir)
        print "Created: %s" % newdir
    if filenames:
        for filename in filenames:
            if not filename.endswith('.pyc'):
                infile = os.path.join(original_dirpath, filename)
                related_infile = os.path.join(relative_dirpath_src, filename)
                if filename == 'README.txt':
                    filename = '%s.%s' % (filename[:-4], readme_ext)
                newfile = filename.replace('__module__', module)
                outfile = os.path.join(replaced_dirpath, newfile)
                print "Read: %s" % infile
                if filename != 'runtests.sh':
                    template = env.get_template(related_infile) 
                    output = template.render(**context).encode('utf-8')
                    codecs.open(outfile, 'w', 'utf-8').write(output)
                else:
                    template = codecs.open(infile, 'r', 'utf-8').read()
                    codecs.open(outfile, 'w', 'utf-8').write(template)
                print "Wrote: %s" % outfile
                