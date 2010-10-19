import os
import shutil
import urllib2
import urlparse
import zipfile
import StringIO

from hurry.resource import generate_code, ResourceInclusion, Library
from hurry.jquery import jquery

VERSION = '0.9.7'
BASEURL = "http://bitbucket.org/cleonello/jqplot/downloads/"


DEPENDENCIES = {'canvasAxisLabelRenderer':['canvasTextRenderer'],
                'canvasAxisTickRenderer':['canvasTextRenderer']}

def prepare_jqplot():
    package_dir = os.path.dirname(__file__)
    jqplot_dest_path = os.path.join(package_dir, 'jqplot-build')

    # remove previous raphael library build
    print 'recursivly removing "%s"' % jqplot_dest_path
    shutil.rmtree(jqplot_dest_path, ignore_errors=True)
    print 'create new "%s"' % jqplot_dest_path
    os.mkdir(jqplot_dest_path)

    filename = 'jquery.jqplot.%s.zip' % VERSION
    url = urlparse.urljoin(BASEURL, filename)
    print 'downloading "%s"' % url
    f = urllib2.urlopen(url)
    file_data = StringIO.StringIO(f.read())
    f.close()
    
    plugins = {} 
    
    archive = zipfile.ZipFile(file_data, 'r')
    for filename in archive.namelist():
        if '/examples/' in filename: continue
        if '.txt' in filename: continue
        if 'jquery-' in filename: continue
        
        outfilename = os.path.join(*filename.split('/')[1:])
        if not outfilename : continue

        dest_filename = os.path.join(jqplot_dest_path, outfilename)
        if filename.endswith('/'):
            print 'Creating directory %s' % dest_filename
            os.mkdir(dest_filename)
            pass
        elif filename.split('.')[-1] not in ['css', 'js']:
            continue
        else:
            if '/plugins/' in filename:
                name = filename.split('/')[-1]
                type = name.endswith('.min.js') and 'mini' or 'full'
                plugins.setdefault(name.split('.')[1], {})[type] = 'plugins/%s' % name
            dest = open(dest_filename, 'wb')
            print 'writing data to "%s"' % dest_filename
            dest.write(archive.read(filename))
            dest.close()
            
    py_path = os.path.join(package_dir, '_lib.py')
    print 'Generating inclusion module "%s"' % py_path

    library = Library('jqplot')
    inclusion_map = {} 
#    inclusion_map['jquery'] = jquery
    base = inclusion_map['base'] = ResourceInclusion(library, 
                                            'jquery.jqplot.js', 
                                            minified='jquery.jqplot.min.js',
#                                            depends = [jquery]
                                            )
    inclusion_map['css'] = ResourceInclusion(library, 
                                            'jquery.jqplot.css', 
                                            minified='jquery.jqplot.min.css')
    inclusion_map['excanvas'] = ResourceInclusion(library, 
                                            'excanvas.js', 
                                            minified='excanvas.min.js')
    
    while plugins:
        for name, files in plugins.items():
            depends = [base]
            if name in DEPENDENCIES:
                if not set(DEPENDENCIES[name]).issubset(set(inclusion_map)):
                    continue
                depends += map(lambda x: inclusion_map[x], DEPENDENCIES[name])   
            inclusion_map[name] = ResourceInclusion(library,
                                                    files['full'],
                                                    minified=files['mini'],
                                                    depends = depends)
            del plugins[name]
            
    code = generate_code(**inclusion_map)
    module = open(py_path, 'w')
    module.write(code)
    module.close()


def main():
    # Commandline tool
    prepare_jqplot()


def entrypoint(data):
    """Entry point for zest.releaser's prerelease script"""
    # We could grab data['new_version'] and omit the .1 suffix from it to get
    # the jqplot version.  Could do away with a bit of version number
    # duplication.
    # And grab the tagdir or workingdir as base, perhaps.
    prepare_jqplot()
