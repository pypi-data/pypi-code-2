import sys, datetime, os, os.path, fnmatch, shutil, re, subprocess
import locale, codecs
from difflib import context_diff
from nts.ntsRC import *
from nts.ntsVersion import version
from platform import system
platform = system()

ntsrc = os.path.join(os.path.expanduser("~"), '.nts', 'rc')
if os.path.exists(ntsrc):
    ntsrc_fo = open(ntsrc, 'r')
    exec(ntsrc_fo)
    ntsrc_fo.close()
else:
    print "Could not find %s. Using defaults." % ntsrc
    font_size = 12

try:
    # try using the user's default settings.
    locale.setlocale(locale.LC_ALL, '')
except:
    # use the current setting for locale.LC_ALL
    locale.setlocale(locale.LC_ALL, None)
    
note_regex = re.compile(r'^\+\s+([^\(]+)\s*(\(([^\)]*)\))?\s*$')
comment_regex = re.compile(r'^\s*#')
empty_regex = re.compile(r'^\s*$')
leadingspaces = re.compile(r'^(\s*)\S.*')

options = {}


today = datetime.date.today()
lastyear = str(int(today.strftime("%Y"))-1)
thismonth = today.strftime("%m")
thisyear = today.strftime("%Y")

if thisyear == '2010':
    copyright = '2010'
else:
    copyright = '2010-%s' % thisyear

def ntsinfo():
    ntsinfo = "ntsdir: %s; ntsdata: %s" % (ntsdir, ntsdata)
    return(ntsinfo)


try:
    from os.path import relpath
except ImportError: # python < 2.6
    from os.path import curdir, abspath, sep, commonprefix, pardir, join
    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = abspath(start).split(sep)
        path_list = abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)

def OpenWithDefault(path):
    if platform in ('Windows', 'Microsoft'):
        os.startfile(path)
    elif platform == 'Darwin':
        import subprocess
        subprocess.Popen('/usr/bin/open' + " %s" % path, shell = True)
    else:
        import subprocess
        subprocess.Popen('xdg-open' + " %s" % path, shell = True)

def get_filelist(topdir=ntsdata, pattern='[!.]*.txt'):
    """yield the list of files in topdir and its subdirectories whose names match pattern."""
    filelist = []
    for path, subdirs, names in os.walk(topdir):
        for name in names:
            if fnmatch.fnmatch(name, pattern):
                full_path = os.path.join(path,name)
                rel_path = relpath(full_path, topdir)
                filelist.append((rel_path, full_path))
    return(filelist)

def process_file(rel_path, full_path):
    i2n = {}
    i2p = {}
    r2p = {}
    r2i = {}
    t2i = {}
    pathname, ext = os.path.splitext(rel_path)
    context = []
    head = pathname
    while head:
        head, tail = os.path.split(head)
        context.insert(0, tail)
    path = tuple(context)
    r2p[rel_path] = path
    f = codecs.open(full_path, 'r', encoding, 'replace')
    note = {}
    line_num = 0
    for line in f:
        line = line.rstrip()
        line_num += 1
        if note_regex.match(line):
            if note:
                # end previous note
                note_end = line_num - 1
                note_id = (rel_path, note_beg, note_end)                        
                note['id'] = note_id
                i2n[note_id] = note
                i2p[note_id] = path
                for tag in note['tags']:
                    t2i.setdefault(tag, []).append(note_id)
                r2i.setdefault(rel_path, []).append(note_id)
                while len(note['text']) > 0 and len(note['text'][-1]) == 0:
                    note['text'].pop()
                note = {}
            m = note_regex.match(line)
            note = {'path' : path}
            note['description'] = m.group(1).strip()
            note['text'] = []
            note_beg = line_num
            try:
                tags = [x.strip() for x in m.group(3).split(',')]
                note['tags'] = tags
            except:
                note['tags'] = []
        else: # must be a note text line
            if note:
                note['text'].append(line)
    if note:
        note_end = line_num
        note_id = (rel_path, note_beg, note_end)                        
        note['id'] = note_id
        while len(note['text']) > 0 and len(note['text'][-1]) == 0:
            note['text'].pop()
        i2n[note_id] = note
        i2p[note_id] = path
        r2i.setdefault(rel_path, []).append(note_id)
        if note['tags']:
            for tag in note['tags']:
                t2i.setdefault(tag, []).append(note_id)
        else:
            t2i.setdefault('none', []).append(note_id)
    return(i2n, i2p, r2p, r2i, t2i)

def process_data(hofh = {}):
    # note = (description, note_lines, tags, id) 
    # where id = (rel_path, beg_line, end_line)
    id2note = {}
    id2pth = {}
    rel2pth = {}
    rel2ids = {}
    tag2ids = {}
    for rel_path, full_path in get_filelist():
        if '_node.txt' in rel_path:
            # TODO: content for the node goes here 
            continue
        mtime = os.path.getmtime(full_path)
        if rel_path not in hofh or hofh[rel_path][0] < mtime:
            lst = process_file(rel_path, full_path)
            hofh[rel_path] = [mtime, lst]
    for mtime, [i2n, i2p, r2p, r2i, t2i] in hofh.values():
        id2note.update(i2n)
        id2pth.update(i2p)
        rel2pth.update(r2p)
        for key in r2i:
            rel2ids.setdefault(key, []).extend(r2i[key])
        for key in t2i:
            tag2ids.setdefault(key, []).extend(t2i[key])
    return(id2note, id2pth, rel2pth, rel2ids, tag2ids, hofh)
            
def make_tree(options, filters):
    # lofl: [nodes] 
    # where each node = [title, [content], [tags], (id), (path)]
    display = ["%s: %s" % (key, options[key]) for key in options.keys() if options[key] ]
    if display:
        display.sort()
        hdr = "; ".join(display)   
    lofl = []
    if options['outlineby'] == 't':
        tags = tag2ids.keys()
        if tags:
            tags.sort()
            for tag in tags:
                if filters['tag_regex']:
                    r = filters['tag_regex'].search(tag)
                    t_res = (r and r.group(0).strip())
                    if (filters['neg_tag'] and t_res):
                        continue
                    if not filters['neg_tag'] and not t_res:
                        continue
                notes = []
                for id in tag2ids[tag]:
                    note = id2note[id]
                    if filter_note(filters, note):
                        path = [tag]
                        # put a lowercase description first for sorting
                        notes.append([note['description'].lower(), note['description'], note['text'], note['tags'], note['id'], path])
                # sort by the first, lower case term
                # notes.sort(key = lambda a:a[0])
                notes.sort()
                # now remove the first, lower case term
                lofl.extend([note[1:] for note in notes])
    else:
        rels = rel2pth.keys()
        if rels:
            # hopefully unicode will not be a problem in the paths
            rels.sort(key = str.lower)
            for rel in rels:
                if filters['path_regex']:
                    r = filters['path_regex'].search(rel)
                    c_res = (r and r.group(0).strip())
                    if (filters['neg_path'] and c_res):
                        continue
                    if not filters['neg_path'] and not c_res:
                        continue
                matching_ids = []
                notes = []
                for id in rel2ids[rel]:
                    note = id2note[id]
                    if filter_note(filters, note):
                        rel_path, beg_line, end_line = note['id'] # id
                        path = split_path(rel_path)
                        # put a lowercase description first for sorting
                        notes.append([note['description'].lower(), note['description'], note['text'], note['tags'], note['id'], path])
                # sort by the first, lower case term
                # notes.sort(key = lambda a:a[0])
                notes.sort()
                # now remove the first, lower case term
                lofl.extend([note[1:] for note in notes])
    return(lofl)


def split_path(rel_path):
    path = []
    head, ext = os.path.splitext(rel_path)
    while head:
        head, tail = os.path.split(head)
        path.insert(0, tail)
    return(path)

def print_tree(tree):
    # note = (note_lines, tags, id) 
    # where id = (rel_path, beg_line, end_line)
    paths = []
    if int(options['details']) > 0:
        ret = "\n"
    else:
        ret = ""
    for note in tree:
        rel_path, beg_line, end_line = note[3] # id
        path = note[4]
        for i in range(len(path)+1):
            part = path[:i]
            if part and part not in paths:
                paths.append(part)
                print "%s%s%s" % (ret, '    '*i,  part[-1])
        print "%s%s%s" % (ret, '    '*(i+1), note[0])
        if int(options['details']) > 0:
            for line in note[1]:
                print "%s%s" % ('    '*(i+2), line)
        if int(options['details']) > 1:
            if note[1]:
                tag_str = "; tags: %s" % ", ".join(note[2])
            else:
                tag_str = ""
            print "%s-- id: %s%s" % ('    '*(i+2),
                ':'.join(map(str,note[3])), tag_str)

                    
def has(hash, key):
    "Return true if key and hash and key in hash and hash[key]"
    try:
        # return(key and hash and key in hash and hash[key] != None)
        return(key and hash and key in hash and 
            hash[key] not in [None, '', {}])
    except:
        print 'except', key, hash
        return(False)
        
def full_path(rel_path):
    return os.path.join(ntsdata, rel_path)

def get_filters(options):
    filter = {}
    if has(options,'find'):
        if options['find'][0] == '!':
            filter['neg_find'] = True
            filter['find_regex'] = re.compile(r'%s' %
                options['find'][1:].decode(encoding), re.IGNORECASE)
        else:
            filter['neg_find'] = False
            filter['find_regex'] = re.compile(r'%s' %
                options['find'].decode(encoding), re.IGNORECASE)
    else:
        filter['neg_find'] = False
        filter['find_regex'] = None   
    if has(options,'path'):
        if options['path'][0] == '!':
            filter['neg_path'] = True
            filter['path_regex'] = re.compile(r'%s' % 
                options['path'][1:].decode(encoding), re.IGNORECASE)
        else:
            filter['neg_path'] = False
            filter['path_regex'] = re.compile(r'%s' % 
                options['path'].decode(encoding), re.IGNORECASE)
    else:
        filter['neg_path'] = False
        filter['path_regex'] = None
    if has(options,'tag'):
        if options['tag'][0] == '!':
            filter['neg_tag'] = True
            filter['tag_regex'] = re.compile(r'%s' %
                options['tag'][1:].decode(encoding), re.IGNORECASE)
        else:
            filter['neg_tag'] = False
            filter['tag_regex'] = re.compile(r'%s' %
                options['tag'].decode(encoding), re.IGNORECASE)
    else:
        filter['neg_tag'] = False
        filter['tag_regex'] = None
    return(filter)
                    
def filter_note(filters, note):
    if filters['find_regex']:
        # include the note description in the text 
        s = "%s %s" % (note['description'], " ".join(note['text']))
        r = filters['find_regex'].search(s)
        s_res = (r and r.group(0).strip())
        if (filters['neg_find'] and s_res):
            return(False)
        if not filters['neg_find'] and not s_res:
            return(False)
    if filters['path_regex']:
        r = filters['path_regex'].search(" ".join(note['path']))
        c_res = (r and r.group(0).strip())
        if (filters['neg_path'] and c_res):
            return(False)
        if not filters['neg_path'] and not c_res:
            return(False)
    if filters['tag_regex']:
        t_res = False
        if has(note, 'tags'):
            # r = filters['tag_regex'].search(" ".join(note['tags']))
            # t_res = (r and r.group(0).strip())
            # if t_res:
            #     return(True)
            for tag in note['tags']:
                r = filters['tag_regex'].search(tag)
                t_res = (r and r.group(0).strip())
                if t_res:
                    break
        if (filters['neg_tag'] and t_res):
            return(False)
        if not filters['neg_tag'] and not t_res:
            return(False)
    return(True)

def noteAdd(rel_path, new_lines):
    file = full_path(rel_path)
    if os.path.exists(file):
        backup(file)
    fo = codecs.open(file, 'a', encoding, 'replace')
    fo.writelines(new_lines)
    fo.close()
    logaction(file, [], new_lines)
    return(True)

def noteReplace(id, new_lines):
    rel_path, line_beg, line_end = id
    file = full_path(rel_path)
    backup(file)
    fo = codecs.open(file, 'r', encoding, 'replace')
    lines = fo.readlines()
    fo.close()
    # leave any blank lines here to keep line numbers correct
    tolines = ["%s\n" % x.rstrip() for x in lines]
    fromlines = ["%s\n" % x.rstrip() for x in lines]
    del tolines[line_beg-1:line_end]
    for i in range(len(new_lines)):
        tolines.insert(line_beg -1 + i, "%s\n" % new_lines[i].rstrip())
    fo = codecs.open(file, 'w', encoding, 'replace')
    fo.writelines(tolines)
    fo.close()
    logaction(file, fromlines, tolines)
    return(True)

def noteDelete(id):
    rel_path, line_beg, line_end = id
    file = full_path(rel_path)
    backup(file)
    fo = codecs.open(file, 'r', encoding, 'replace')
    lines = fo.readlines()
    fo.close()
    tolines = ["%s\n" % x.rstrip() for x in lines]
    fromlines = ["%s\n" % x.strip() for x in lines]
    del tolines[line_beg-1:line_end]
    # are there any other notes?
    empty = True
    for line in tolines:
        if line.strip():
            empty = False
            break
    if empty:
        os.remove(file)
        res = 2
    else:
        tolines.insert(line_beg-1, '\n')
        fo = codecs.open(file, 'w', encoding, 'replace')
        fo.writelines(tolines)
        fo.close()
        res = 1
    logaction(file, fromlines, tolines)
    return(res)

def backup(file):
    pathname, ext = os.path.splitext(file)
    directory, name = os.path.split(pathname)
    bak = os.path.join(directory, ".%s.bk1" % name)
    if os.path.exists(bak):
        m_secs = os.path.getmtime(bak)
        m_date = datetime.date.fromtimestamp(m_secs)
    else:
        m_date = None
    # only backup if there is no backup or it is at least one day old
    if not m_date or m_date < datetime.date.today():
        for i in range(1, numbaks):
            baknum = numbaks - i
            nextnum = baknum + 1
            bakname = os.path.join(directory,".%s.bk%d" % (name, baknum))
            if os.path.exists(bakname):
                nextname = os.path.join(directory,".%s.bk%d" % (name,
                 nextnum))
                shutil.move(bakname, nextname)
        shutil.copy2(file, bak)
        return(True)
    return(False)
    
def logaction(file, fromlines, tolines):
    pathname, ext = os.path.splitext(file)
    directory, name = os.path.split(pathname)
    logfile = os.path.join(directory, ".%s.log" % name)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fo = codecs.open(logfile, 'a', encoding, 'replace')
    fo.write("%s\n" % now)
    for line in context_diff(fromlines, tolines, fromfile="old",
        tofile="new", n=0):
        if line.strip():
            fo.write("    %s\n" % line.rstrip())
    fo.close()
    return(True)
    

def get_opts():
    from optparse import OptionParser
    parser = OptionParser(version = "nts %s" % version,
        description = "Manage notes using simple text files. (C) %s Daniel A Graham." % copyright)

    parser.add_option("-o", action = "store",
        dest='outlineby',  choices = ['p', 't'], default = 'p',
        help = """An element from [p, t] where:	                          \n
        p: outline by path								                  \n
        t: outline by tag							                      \n
        Default: %default.""")
    parser.add_option("-p", action = "store",
        dest='path',
        help = """Regular expression. Include items with paths matching PATH (ignoring case). Prepend an exclamation mark, i.e., use !PATH rather than PATH, to include items which do NOT have contexts matching PATH.""")
    parser.add_option("-t", action = "store",
        dest='tag',
        help = """Regular expression. Include items with tags matching TAG (ignoring case). Prepend an exclamation mark, i.e., use !TAG rather than TAG, to include items which do NOT have tags matching TAG.""")
    parser.add_option("-f", 
        action="store",
        dest='find',
        help = """Regular expression. Include items containing FIND (ignoring case) in the note text. Prepend an exclamation mark, i.e., use !FIND rather than FIND, to include notes which do NOT have note texts matching FIND.""")
    parser.add_option("-d", "--details",
        action="store", dest="details", 
        choices = ['0', '1', '2'], default = '1', 
        help="""An element from [0, 1, 2] where:                            
        0: only show note descriptions                                       
        1: also show note text                                               
        2: also show note id and tags                                       
        Default: %default.""")
    
    (opts, args) = parser.parse_args()
    return(opts.__dict__)

def load_data(hofh = {}):
    global id2note, id2pth, rel2pth, rel2ids, tag2ids
    id2note, id2pth, rel2pth, rel2ids, tag2ids, hofh = process_data(hofh)
    return(hofh)

def main():
    global options, filters
    options = get_opts()
    filters = get_filters(options)
    load_data()
    lofl = make_tree(options, filters)
    print_tree(lofl)
    
if __name__ == '__main__':
    main()