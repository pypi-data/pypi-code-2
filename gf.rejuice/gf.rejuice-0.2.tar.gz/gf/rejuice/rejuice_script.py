"""Rejuice
Construct or reconstruct all resources with juicer
"""
import sys
import os
import subprocess
import re
from urlparse import urlparse
import shutil

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
from resolver import ResolverList

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def run_juicer(resources, output):
    attrs = ('juicer', 'merge', '-i', '--force', '-o', output) + resources
    print '##### Will run: ' + ' '.join(attrs) 
    # check the file... because juicer does not give an error if it is missing.
    
    for resource in resources:
        file(resource).close()
    status = subprocess.call(attrs)
    if status != 0:
        print "\n\n##### ERROR: FAILED compression of " + output
        print '\nTry to consolidate problems by running manually:\n\n' + ' '.join(attrs) + '\n'
        raise SystemExit, "Compression of " + output + " failed"

def run_replace_url(output, prod_resource_path):
    infile = open(output, 'r')
    outfile = open(prod_resource_path, 'w')
    resource_prefix = os.path.basename(prod_resource_path) + '.images/'
    result = replace_url(output, infile, outfile, resource_prefix)
    infile.close()
    outfile.close()
    return result

def copy_images(images, prod_resource_path):
    dirname = prod_resource_path + '.images'
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)

    for image, newimage in images.iteritems():
        if os.path.isfile(image):
            shutil.copy(image, os.path.join(dirname, newimage))
        else:
            miss = open(os.path.join(dirname, newimage + '.MISSING'), 'w')
            miss.close()

re_url = re.compile(r"url\([\s\"']*([^\) \"']+)[\s\"']*\)")
def replace_url(infile_name, infile, outfile, resource_prefix):
    
    images = {}
    names = []
    
    def file_replace(match):
        url = match.group(1)
        parse = urlparse(url)
        if parse.netloc:
            return 'url(%s)' % (url, )
        query = parse.query
        if query:
            query = '?' + query
        abs_path = os.path.join(os.path.dirname(infile_name), parse.path)
        abs_path = os.path.abspath(abs_path)
        if abs_path in images:
            return 'url(%s)' % (resource_prefix + images[abs_path] + query)
        filename = os.path.basename(parse.path)
        root, ext = os.path.splitext(filename)
        if filename in names:
            i = 1
            while True:
                file = root + '_' + str(i) + ext
                if file not in names:
                    break;
                i = i + 1 
            filename = root + '_' + str(i) + ext
        images[abs_path] = filename
        names.append(filename)
        result = 'url(%s)' % (resource_prefix + filename + query, )
        return result

    if infile_name.endswith('.css'): 
        for line in infile:
            line = line.rstrip('\n')
            res =re_url.sub(file_replace, line)
            outfile.write(res + '\n')

    return images


def main(argv=sys.argv, 
        run_juicer=run_juicer, run_replace_url=run_replace_url,
        copy_images=copy_images, remove_file=os.remove):
    if len(argv) !=3:
        raise RuntimeError, 'Usage: rejuice inifile section_name'
    inifile = argv[1]
    section_name = argv[2]

    resolver = ResolverList(())
    resolver.add_new_section(inifile, section_name, allow_filter_section_keys=True)
    
    for o in resolver:
        for resource in o.resources:
            prod_resource = resource
            prod_resource_path = os.path.join(o.filepath, prod_resource)
            devel_resources = o.resources[resource]
            devel_resource_path_list = []
            has_import_resource = False
            for devel_resource_spec, extend_inifile, extend_section in devel_resources:
                if extend_inifile is not None:
                    assert extend_section is not None
                    extend_resource = o.sections.get((extend_inifile, extend_section), None)
                    devel_resource_path = os.path.join(extend_resource.filepath, devel_resource_spec)
                    # Is this a resource imported from another static tree?
                    if extend_resource.filepath != o.filepath:
                        has_import_resource = True
                else:
                    assert extend_section is None
                    devel_resource_path = os.path.join(o.filepath, devel_resource_spec)
                devel_resource_path_list.append(devel_resource_path)
            # Do we have to collect the images to this resource?
            if has_import_resource and prod_resource_path.endswith('css'):
                # import mode
                output = os.tmpnam() + '.css'
                try:
                    run_juicer(tuple(devel_resource_path_list), output=output)
                    images = run_replace_url(output, prod_resource_path)
                finally:
                    try:
                        remove_file(output)
                    except (OSError, IOError):
                        pass
                copy_images(images, prod_resource_path)
            else:
                # run external program to do the concatenation
                run_juicer(tuple(devel_resource_path_list), output=prod_resource_path)
                
                

    print "\n\n##### All files compressed OK"



if __name__ == '__main__':
    main()
