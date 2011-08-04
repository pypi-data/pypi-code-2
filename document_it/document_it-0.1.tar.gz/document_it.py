#!/usr/bin/env python

"""
update MDN documentation from markdown

see:
http://developer.mindtouch.com/en/ref/MindTouch_API/POST%3Apages%2F%2F%7Bpageid%7D%2F%2Fcontents

The manifest format is in the form:

mozrunner/README.txt  https://developer.mozilla.org/en/Mozrunner
jsbridge/README.txt   https://developer.mozilla.org/en/JSbridge
mozmill/README.txt    https://developer.mozilla.org/en/Mozmill
mozmill/docs/         https://developer.mozilla.org/en/Mozmill/

--dest sets the destination.  If a net location is specified, authentication
is required. By default, a new temporary directory will be created
"""

import optparse
import os
import sys
import tempfile
import urllib2

# import markdown
try:
    import markdown
except ImportError:
    raise ImportError("markdown is not installed, run (e.g.):\neasy_install Markdown")

destinations = {'stage': 'https://developer-stage9.mozilla.org/@api/deki/pages/=%(page)s/contents?edittime=now',
                'MDN': 'https://developer.mozilla.org/@api/deki/pages/=%(page)s/contents?edittime=now'}


def find_readme(directory):
    """find a README file in a directory"""
    # XXX currently unused
    README=['README.md', 'README.txt', 'README']
    for name in README:
        path = os.path.join(directory, name)
        if os.path.exists(path):
            return path

def all_files(directory):
    """get all files in a directory tree"""
    filenames = []
    for dirpath, dirnames, files in os.walk(directory):
        filenames.extend([os.path.join(dirpath, f) for f in files])
    return sorted(filenames)
                    
def parse_manifest(filename, directory=None):
    """
    reads a documentation manifest; returns a list of two-tuples:
    [(filename, destination)]
    """
    
    assert os.path.exists(filename) and os.path.isfile(filename), "%s not found" % filename
    
    if directory is None:
        directory = os.path.dirname(os.path.abspath(filename))
    lines = [line.strip() for line in file(filename).readlines()]
    lines = [line for line in lines
             if line and not line.startswith('#')]
    items = []
    for line in lines:
        try:
            f, page = line.split()
            # TODO: include options as third segment (e.g. format=ReST)
        except ValueError:
            raise ValueError("illegal manifest line: '%s'" % line)

        filename = os.path.join(directory, f)
        if os.path.isdir(filename):
            raise NotImplementedError
            files = all_files(filename)
            for i in files:
                relpath = os.path.relpath(i, filename)
                items.append((i, relpath))
        else:
            items.append((filename, page))
    return items

def item_url(item, dest):
    if '://' in dest:
        if '%(page)s' in dest:
            return dest % {'page': item.replace('/', r'%25%32%66')}
        else:
            return '%s/%s' % (dest.lstrip('/'), item.rstrip('/'))
    else:
        return 'file://%s' % (os.path.join(dest, item))


def render(filename):
    """render a file in markdown"""
    return markdown.Markdown().convert(file(filename).read())    

def post(content, url, user, password):
    """post to the specified URL"""
    # XXX cheat and use curl for now
    try:
        from subprocess import check_call as call
    except:
        from subprocess import call
    content = content.replace('\r', '').replace('\n', '\r\n') # just to make sure
    fd, filename = tempfile.mkstemp()
    os.write(fd, content)
    os.close(fd)
    command = ["curl", "-u", "%s:%s" % (user, password),
               "--data-binary", "@%s" % filename,
               "-i", url]
    call(command)
    os.remove(filename)

def main(args=sys.argv[1:]):

    # default output directory
    default_dir = tempfile.mktemp()

    # parse command line options
    usage = '%prog [options] manifest <manifest> <...>'

    # description formatter
    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        def format_description(self, description):
            if description:
                return description.strip() + '\n'
            else:
                return ''
    
    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    parser.add_option('-d', '--directory', dest='directory',
                      help='render the documentation from this directory')
    parser.add_option('-o', '--dest', dest='dest',
                      default=default_dir,
                      help='base directory or URL of destination [DEFAULT: %default]')
    parser.add_option('-u', '--user', dest='user',
                      help='user name')
    parser.add_option('-p', '--password', dest='password',
                      help='user password')
    parser.add_option('--list', dest='list', action='store_true', default=False,
                      help="list files")
    parser.add_option('-l', '--list-destinations', dest='list_destinations',
                      action='store_true', default=False,
                      help='list preconfigured destinations')
    parser.add_option('--validate', dest='validate', # TODO unused
                      action='store_true', default=False,
                      help="validate the rendering but don't output")
    options, manifests = parser.parse_args(args)

    # print help if no manifests given
    if not args:
        parser.print_help()
        parser.exit()

    # print preconfigured destinations if asked
    if options.list_destinations:
        for key in sorted(destinations.keys()):
            print '%s: %s' % (key, destinations[key])
        return # you're done

    # get destination
    assert options.dest
    if options.dest in destinations:
        options.dest = destinations[options.dest]
    if options.dest.startswith('file://'):
        options.dest = options.dest[len('file://'):]
    if '://' not in options.dest:
        options.dest = os.path.abspath(options.dest)

    # read the manifests
    files = []
    for manifest in manifests:
        for item in parse_manifest(manifest, options.directory):
            if item not in files:
                files.append(item)
    files = [(i, item_url(j, options.dest)) for i, j in files]
    if options.list:
        for item in files:
            print '%s -> %s' % item
        return

    if not files:
        return # you're done

    # render and upload READMEs
    if '://' in options.dest:
        
        # check credentials
        assert options.user and options.password, "Please supply your --user and --password"

        # upload the files
        for src, dest in files:
            post(render(src), dest, options.user, options.password)

    else:

        # ensure a directory
        if os.path.exists(options.dest):
            assert os.path.isdir(options.dest), "'%s' - not a directory" % options.dest

        # render to directory
        for src, dest in files:
            
            if dest.startswith('file://'):
                dest = dest[len('file://'):]

            # create a directory if needed
            dirname = os.path.dirname(dest)
            if os.path.exists(dirname):
                if not os.path.isdir(dirname):
                    # deal with filesystem directories vs PATH_INFO
                    f = file(dirname)
                    buffer = f.read()
                    f.close()
                    os.remove(dirname)
                    os.makedirs(dirname)
                    f = file(os.path.join(dirname, 'index.html'), 'w')
                    f.write(buffer)
                    f.close()
            else:
                os.makedirs(dirname)

            # render
            f = file(dest, 'w')
            f.write(render(src))
            f.close()

    # print out destination directory if using the temporary default
    if options.dest == default_dir:
        print "Files rendered to\n%s" % default_dir

if __name__ == '__main__':
    main()
