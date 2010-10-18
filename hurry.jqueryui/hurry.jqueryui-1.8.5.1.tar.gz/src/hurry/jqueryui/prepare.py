import py
import os
import sys
import urllib2
import urlparse
import tempfile
from hurry.resource import generate_code, ResourceInclusion, Library

from hurry.jquery import jquery

BASEURL = 'http://ajax.googleapis.com/ajax/libs/jqueryui/'
VERSION = '1.8.5'
MINIFIED = "jquery-ui.min.js"
FULL = "jquery-ui.js"
THEME_URL = 'http://jquery-ui.googlecode.com/files/jquery-ui-themes-%s.zip' % VERSION

def prepare_jqueryui(package_dir):
    jquery_dest_path = package_dir.join('jqueryui-build')

    # remove previous jquery library build
    print 'recursively removing "%s"' % jquery_dest_path
    if jquery_dest_path.check():
        jquery_dest_path.remove()
    print 'create new "%s"' % jquery_dest_path
    jquery_dest_path.ensure(dir=True)
    
    for filename in [MINIFIED, FULL]:
        url = urlparse.urljoin(BASEURL + VERSION + '/', filename)
        print 'downloading "%s"' % url
        f = urllib2.urlopen(url)
        file_data = f.read()
        f.close()
        dest_file = jquery_dest_path.join(filename)
        print 'writing data to "%s"' % dest_file
        dest_file.write(file_data)
    
    # now set up themes
    print "remove previous themes"
    themes_dest_path = package_dir.join('jqueryui-themes')
    if themes_dest_path.check():
        themes_dest_path.remove()
 
    print "downloading themes"
    f = urllib2.urlopen(THEME_URL)
    file_data = f.read()
    f.close()

    temp_dir = py.path.local.mkdtemp()
    
    zip_file = temp_dir.join('zipfile.zip')
    zip_file.write(file_data)
    
    print "unzipping themes"
    unzip_dir = temp_dir.join('unzipped')
    os.system('unzip -qq "%s" -d "%s"' % (zip_file, unzip_dir.strpath))

  
    print "copying themes"
    try:
        for dir in unzip_dir.listdir():
            if dir.check(dir=True):
                themes_dir = dir.join('themes')
                break
        themes_dir.copy(themes_dest_path)
    finally:
        temp_dir.remove()

    print "generating theme information"
    py_path = package_dir.join('_themes.py')
    print 'Generating inclusion module "%s"' % py_path

    library = Library('jqueryui_themes', 'jqueryui-themes')
    inclusion_map = {}
    for theme in themes_dest_path.listdir():
        if not theme.check(dir=True):
            continue
        if theme.basename.startswith('.'):
            continue
        theme_name = str(theme.basename)
        python_theme_name = theme_name.replace('-', '_')
        inclusion = inclusion_map[python_theme_name] = ResourceInclusion(
            library, '%s/jquery-ui.css' % theme_name)

    code = generate_code(**inclusion_map)
    module = py_path.open('w')
    module.write(code)
    module.close()

def main():
    prepare_jqueryui(py.path.local(os.path.dirname(__file__)))

def working_entrypoint(data):
    if data['name'] != 'hurry.jqueryui':
        return
    prepare_jqueryui(py.path.local(os.path.dirname(__file__)))

def tag_entrypoint(data):
    if data['name'] != 'hurry.jqueryui':
        return
    prepare_jqueryui(py.path.local(data['tagdir'] + '/src/hurry/jqueryui'))
