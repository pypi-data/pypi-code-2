import sys, datetime, os, os.path, fnmatch, shutil, re, subprocess
import locale, codecs
# import base64               # for crypt
from base64 import b64encode, b64decode
from dateutil.tz import tzlocal, tzutc

from nts.ntsRC import *
from nts.ntsVersion import version
from platform import system
platform = system()


try:
    # try using the user's default settings.
    locale.setlocale(locale.LC_ALL, '')
except:
    # use the current setting for locale.LC_ALL
    locale.setlocale(locale.LC_ALL, None)

if editor and not EDITOR:
    EDITOR = editor
if editcmd and not EDITCMD:
    EDITCMD = editcmd

note_regex = re.compile(r'^\+\s+([^\(]+)\s*(\(([^\)]*)\))?\s*$')
comment_regex = re.compile(r'^\s*#')
empty_regex = re.compile(r'^\s*$')
leadingspaces = re.compile(r'^(\s*)\S.*')

regex_end = re.compile(r'^\s*!\s*$')
regex_datetime = re.compile(r'!d')

messages =[]
warning = "" 
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

def get_newer():
    global version
    from urllib import urlopen, urlretrieve
    # strip the '-x' from experimental versions
    version = (version.split('-'))[0]
    try:
        vstr = urlopen(
            "http://www.duke.edu/~dgraham/NTS/version.txt").read().strip()
        if int(version) < int(vstr): 
            return(1, 'A newer release of nts, version %s, is available.' % (vstr))
        else:
            return(1, '')
    except:
        return(0, '')

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
        subprocess.Popen('/usr/bin/open' + " %s" % path, shell = True)
    else:
        subprocess.Popen('xdg-open' + " %s" % path, shell = True)

def get_filelist(topdir=ntsdata, txtpattern='[!.]*%s' % ntstxt,
    encpattern='[!.]*%s' % ntsenc):
    """yield the list of files in topdir and its subdirectories whose names match pattern."""
    filelist = []
    for path, subdirs, names in os.walk(topdir):
        for name in names:
            if (fnmatch.fnmatch(name, txtpattern) or
                fnmatch.fnmatch(name,encpattern)):
                full_path = os.path.join(path,name)
                rel_path = relpath(full_path, topdir)
                filelist.append((rel_path, full_path))
    return(filelist)

def crypt(str):
    str = str.rstrip('\n')
    # print "crypt orig: '%s'" % str
    if str.endswith("="):
        # shouldn't happen
        return(str)
    if str:
        # add a starting ! to reserve leading white space
        str = "!%s" % str
    retval = b64encode(str.encode(encoding)).rstrip('\n')
    #  retval = b64encode(str).rstrip('\n')
    if retval and not retval.endswith('='):
        # make sure we have an ending =
        retval = "%s=" % retval
    return(retval)

def decrypt(str):
    str = str.rstrip('\n')
    try:
        retval = unicode(b64decode(str), encoding)
    except:
        print "bad string: '%s'" % str
        retval = None
    if retval:
        # drop the starting !
        retval = retval[1:]
    return(retval)

def CryptLines(lines):
    return(["%s\n" % crypt(x) for x in lines])

def DeCryptLines(lines):
    return(["%s\n" % decrypt(x) for x in lines])

def ConvertFile(orig_file, new_file, tocrypted = True, remove_orig = True):
    '''If plain text convert to encrypted, else convert encrypted to plain text'''
    fo = codecs.open(orig_file, 'r', encoding, 'replace')
    f = fo.readlines()
    fo.close()
    lines = []
    for line in f:
        line = line.rstrip('\n')
        if tocrypted:
            lines.append(crypt(line))
        else:
            lines.append(decrypt(line))
    fo = codecs.open(new_file, 'w', encoding, 'replace')
    fo.writelines(["%s\n" % x for x in lines])
    fo.close()
    if remove_orig:
        os.remove(orig_file)
    return(True)

def process_file(rel_path, full_path):
    # print "process_file", rel_path
    global messages
    i2n = {}
    i2p = {}
    r2p = {}
    r2i = {}
    t2i = {}
    pathname, ext = os.path.splitext(rel_path)
    if ext == ntsenc:
        encrypt = True
    else:
        encrypt = False
    context = []
    head = pathname
    while head:
        head, tail = os.path.split(head)
        context.insert(0, tail)
    path = tuple(context)
    r2p[rel_path] = path
    fo = codecs.open(full_path, 'r', encoding, 'replace')
    f = fo.readlines()
    fo.close()
    if not f:
        messages.append("skipping %s:\n    could not obtain content" 
                % rel_path)
        return()
    line = f[0].strip()
    if encrypt:
        line = decrypt(line)
    if not note_regex.match(line):
        messages.append("%s:\n    the first line does not begin a note" 
                % rel_path)
        return()
    note = {}
    line_num = 0
    try:
        for line in f:
            line = line.rstrip('\n')
            if encrypt:
                line = decrypt(line)
            line_num += 1
            if note_regex.match(line):
                if note:
                    # end previous note
                    note_end = line_num - 1
                    note_id = (rel_path, note_beg, note_end) 
                    # print "set id", note_id
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
                if m.group(3):
                    try:
                        tags = [x.strip() for x in m.group(3).split(',')]
                        note['tags'] = tags
                    except:
                        note['tags'] = ['none']
                else:
                    note['tags'] = ['none']
            else: # must be a note text line
                if note:
                    note['text'].append(line)
    except:
        note = {}
        messages.append("exception raised processing %s\n    %s" 
                % (rel_path, sys.exc_info()))
        return()
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

def get_relpath(exp = ''):
    if exp:
        regex = re.compile(r'%s' % exp.decode(encoding), re.IGNORECASE)
    else:
        regex = ''
    n = 0
    hsh = {}
    for rel_path, full_path in get_filelist():
        if regex and not regex.match(rel_path):
            continue
        n += 1
        hsh[n] = rel_path
        print "[%s] %s" % (n, rel_path)
    print """\
----------------------------------------------------------------
    Enter the number of an existing file or the relative path
    of an new file to which the new note should be appended.
----------------------------------------------------------------\
    """
    rp = raw_input('> ')
    if len(rp) > 0:
        try:
            rp = hsh[int(rp)]
        except:
            pass
    else:
        rp = ''
    return(rp)

def process_data(hofh = {}):
    # note = (description, note_lines, tags, id) 
    # where id = (rel_path, beg_line, end_line)
    global messages
    messages = []
    id2note = {}
    id2pth = {}
    rel2pth = {}
    rel2ids = {}
    tag2ids = {}
    for rel_path, full_path in get_filelist():
        pathname, ext = os.path.splitext(rel_path)
        mtime = os.path.getmtime(full_path)
        if rel_path not in hofh or hofh[rel_path][0] < mtime:
            lst = process_file(rel_path, full_path)
            if not lst:
                # the problem should already have been appended to messages
                continue
            hofh[rel_path] = [mtime, lst]
    for mtime, [i2n, i2p, r2p, r2i, t2i] in hofh.values():
        id2note.update(i2n)
        id2pth.update(i2p)
        rel2pth.update(r2p)
        for key in r2i:
            rel2ids.setdefault(key, []).extend(r2i[key])
        for key in t2i:
            tag2ids.setdefault(key, []).extend(t2i[key])
    if messages:
        for message in messages:
            print("%s" % message)
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
                        notes.append([note['description'].lower(),
                            note['description'], note['text'], note['tags'],
                            note['id'], path])
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
                        notes.append([note['description'].lower(),
                            note['description'], note['text'], note['tags'],
                            note['id'], path])
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
    display = int(options['display'])
    number = int(options['number'])
    tags = options['outlineby'] == 't'
    if 'lines' in options:
        num_lines = options['lines']
    else:
        num_lines = 0
    if options['edit']:
        edit = options['edit']
    else:
        edit = 0
    if options['editfile']:
        editfile = options['editfile']
    else:
        editfile = 0
    if  options['remove']:
        remove = options['remove']
        #  show everything for confirmation
        display = 7
        num_lines = 4
    else:
        remove = 0
    arglist = []
    if options['args']:
        for arg in options['args']:
            if ':' in arg:
                b, e = map(int, arg.split(':'))
                for i in range(b, e+1):
                    arglist.append(i)
            else:
                arglist.append(int(arg))
    # note = [title, [content], [tags], (id), (path)]
    # where id = (rel_path, beg_line, end_line)
    paths = []
    tab = '  '
    last_tag = ''
    indent = 0
    num_indent = 0
    body_indent = 0
    title_indent = 0
    info_indent = 0
    if display in [3,7]:
        body_indent = 1
    if display in [7]:
        info_indent = 1
    if display == 2 and number == 0:
        ret = True
    else:
        ret = False
    num = 0
    if tags:
        if number:
            num_indent = 1
        else:
            title_indent = 1
        body_indent += 1
        info_indent += 1
    for note in tree:
        num += 1
        if arglist and num not in arglist:
            continue
        if edit and num != edit:
            continue
        if editfile and num != editfile:
            continue
        if remove and num != remove:
            continue
        rel_path, beg_line, end_line = note[3] # id
        path = note[4]
        if display in [1, 3, 5, 7]:
            title = "%s%s" % (tab*title_indent, note[0])
        else:
            title = ""
        if display in [2,3,6,7]:
            if note[1]:
                #  get leading white space
                first = note[1][0]
                ws = len(first) - len(first.lstrip())
                if options['lines']:
                    num_lines = int(options['lines'])
                    omitted = len(note[1])-num_lines
                    if omitted > 1:
                        lines = note[1][:num_lines]
                        while len(lines) > 0 and len(lines[-1].strip()) == 0:
                            lines.pop()
                        lines.append('... (%s omitted lines)' % omitted)
                    else:
                        lines = note[1]

                else:
                    lines = note[1]
                if ws:
                    ws_regex = re.compile(r'^\s{1,%d}' % ws)
                    body = ["%s%s" % (tab*body_indent, ws_regex.sub('', x)) 
                        for x in lines]
                else:
                    body = ["%s%s" % (tab*body_indent, x) 
                        for x in lines]
            else:
                print('error: missing body for note %s' % note[0])
        else:
            body = []
        if display in [4,5,6,7]:
            if note[2] and note[2][0] != 'none':
                tag_str = " (%s)" % ", ".join(note[2])
            else:
                tag_str = ""
            info = "%s-- %s%s" % (tab*info_indent,
                    ':'.join(map(str,note[3])), tag_str)
        else:
            info = ""
        if options['edit']:
            edit_note(note[3])
            return()
        if options['editfile']:
            edit_file(note[3])
            return()
        if remove:
            print"""\
---------------------------------------------------------------------
            The following note is to be removed.
---------------------------------------------------------------------"""
        if tags:
            if path[0] != last_tag:
                last_tag = path[0]
                print "%s" % path[0]
        if number:
            print "%s[%s]" % (tab*num_indent, num),
        if title:
            print "%s%s" % (tab*title_indent, title)
        if body:
            for line in body:
                print line
        if info:
            print info
        if remove:
            print"""\
---------------------------------------------------------------------"""
            confirm = raw_input('Delete this note? [yN] ')
            if confirm.upper() == 'Y':
                noteDelete(note[3])
            else:
                print "Cancelled"
            return()
        if ret:
            print ""


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
            if type(options['find']) == str:
                filter['find_regex'] = re.compile(r'%s' %
                    options['find'][1:].decode(encoding), re.IGNORECASE)
            else:
                filter['find_regex'] = re.compile(r'%s' %
                    options['find'][1:], re.IGNORECASE)
        else:
            filter['neg_find'] = False
            if type(options['find']) == str:
                filter['find_regex'] = re.compile(r'%s' %
                    options['find'].decode(encoding), re.IGNORECASE)
            else:
                filter['find_regex'] = re.compile(r'%s' %
                    options['find'], re.IGNORECASE)
    else:
        filter['neg_find'] = False
        filter['find_regex'] = None 
    if has(options,'path'):
        if options['path'][0] == '!':
            filter['neg_path'] = True
            if type(options['find']) == str:
                filter['path_regex'] = re.compile(r'%s' % 
                    options['path'][1:].decode(encoding), re.IGNORECASE)
            else:
                filter['path_regex'] = re.compile(r'%s' % 
                    options['path'][1:], re.IGNORECASE)

        else:
            filter['neg_path'] = False
            if type(options['find']) == str:
                filter['path_regex'] = re.compile(r'%s' % 
                    options['path'].decode(encoding), re.IGNORECASE)
            else:
                filter['path_regex'] = re.compile(r'%s' % 
                    options['path'], re.IGNORECASE)
    else:
        filter['neg_path'] = False
        filter['path_regex'] = None
    if has(options,'tag'):
        if options['tag'][0] == '!':
            filter['neg_tag'] = True
            if type(options['find']) == str:
                filter['tag_regex'] = re.compile(r'%s' %
                    options['tag'][1:].decode(encoding), re.IGNORECASE)
            else:
                filter['tag_regex'] = re.compile(r'%s' %
                    options['tag'][1:], re.IGNORECASE)
        else:
            filter['neg_tag'] = False
            if type(options['find']) == str:
                filter['tag_regex'] = re.compile(r'%s' %
                    options['tag'].decode(encoding), re.IGNORECASE)
            else:
                filter['tag_regex'] = re.compile(r'%s' %
                    options['tag'], re.IGNORECASE)
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

def datestamps(lines):
    dt_naive = datetime.datetime.now()
    dt_local = dt_naive.replace(tzinfo = tzlocal())
    dt_fmt = dt_local.strftime("%Y-%m-%d %H:%M %Z")
    return [regex_datetime.sub(dt_fmt, l) for l in lines]

def noteAdd(rel_path, new_lines):
    new_lines = datestamps(new_lines)
    file = full_path(rel_path)
    if os.path.exists(file):
        backup(file)
    pathname, ext = os.path.splitext(rel_path)
    if ext == ntsenc:
        new_lines = CryptLines(new_lines)
    fo = codecs.open(file, 'a', encoding, 'replace')
    fo.writelines(["%s\n" % x.rstrip('\n') for x in new_lines])
    fo.close()
    fo = codecs.open(file, 'r', encoding, 'replace')
    num_lines = len(fo.readlines())
    fo.close()
    line_beg = num_lines - len(new_lines) + 1
    return(line_beg)

def noteReplace(id, new_lines):
    new_lines = datestamps(new_lines)
    rel_path, line_beg, line_end = id
    file = full_path(rel_path)
    backup(file)
    pathname, ext = os.path.splitext(rel_path)
    if ext == ntsenc:
        encrypt = True
    else:
        encrypt = False
    fo = codecs.open(file, 'r', encoding, 'replace')
    lines = fo.readlines()
    fo.close()
    # leave any blank lines here to keep line numbers correct
    tolines = ["%s\n" % x.rstrip('\n') for x in lines]
    fromlines = ["%s\n" % x.rstrip('\n') for x in lines]
    if encrypt:
        new_lines = CryptLines(new_lines)
    del tolines[line_beg-1:line_end]
    for i in range(len(new_lines)):
        tolines.insert(line_beg -1 + i, "%s\n" % new_lines[i].rstrip('\n'))
    fo = codecs.open(file, 'w', encoding, 'replace')
    fo.writelines(tolines)
    fo.close()
    return(line_beg)

def noteDelete(id):
    rel_path, line_beg, line_end = id
    file = full_path(rel_path)
    backup(file)
    fo = codecs.open(file, 'r', encoding, 'replace')
    lines = fo.readlines()
    fo.close()
    tolines = ["%s\n" % x.rstrip('\n') for x in lines]
    fromlines = ["%s\n" % x.strip('\n') for x in lines]
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
        if line_beg > 1:
            tolines.insert(line_beg-1, '\n')
        fo = codecs.open(file, 'w', encoding, 'replace')
        fo.writelines(tolines)
        fo.close()
        res = 1
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
        if ext == ntsenc:
            # already encoded
            shutil.copy2(file, bak)
        else:
            # plain text, convert and leave original
            ConvertFile(file, bak, True, False)
        return(True)
    return(False)

def edit_note(id):
    if not EDITOR:
        print "The EDITOR variable must be set in %s to use this option." % ntsdir
        return()
    rel_path, line_beg, line_end = id
    orig_file = full_path(rel_path)
    pathname, ext = os.path.splitext(rel_path)
    if ext == ntsenc:
        decrypting = True
    else:
        decrypting = False
    fo = codecs.open(orig_file, 'r', encoding, 'replace')
    f = fo.readlines()
    fo.close()
    lines = []
    for line in f[line_beg-1:line_end]:
        line = line.rstrip('\n')
        if decrypting:
            lines.append(decrypt(line))
        else:
            lines.append(line)
    new_lines = ext_lines(lines)
    if len(new_lines) < 2:
        print "Cancelled. At least 2 lines must be entered."
        return()
    if new_lines[0][0] != '+':
        print "Cancelled. The first line must begin with '+'."
        return()
    noteReplace(id, new_lines)

def edit_file(id):
    if not EDITOR:
        print "The EDITOR variable must be set in %s to use this option." % ntsdir
        return()
    temp = None
    rel_path, line_beg, line_end = id
    file = full_path(rel_path)
    if file:
        backup(file)
        pathname, ext = os.path.splitext(file)
        if ext == ntsenc:  # encoded, need a plain text copy
            temp = "%s%s" % (pathname, ntstxt)
            ConvertFile(file, temp, False, True) # removes orig
            command = EDITCMD % {'e': EDITOR, 'n': line_beg, 'f': temp}
            os.system(command)
            ConvertFile(temp, file, True, True) # removes temp
        else: # plain text
            command = EDITCMD % {'e': EDITOR, 'n': line_beg, 'f': file}
            os.system(command)

def get_note(quicknote = False):
    if EDITOR:
        lines = ext_lines()
    else:
        lines = raw_lines()
    if len(lines) < 2:
        print "Cancelled. At least 2 lines must be entered."
        return()
    if lines[0][0] != '+':
        print "Cancelled. The first line must begin with '+'."
        return()
    if quicknote:
        rp = quick
    else:
        rp = get_relpath()
    if rp:
        noteAdd(rp, lines)

def ext_lines(orig_lines=[]):
    temp = os.path.join(ntsdir, '.temp')
    fo = codecs.open(temp, 'w', encoding, 'replace')
    if orig_lines:
        for line in orig_lines:
            fo.write("%s\n" % line)
    else:
        fo.write("+ ")
    fo.close()
    command = EDITCMD % {'e': EDITOR, 'n': '1', 'f': temp}
    os.system(command)
    fo = codecs.open(temp, 'r', encoding, 'replace')
    lines = fo.readlines()
    fo.close()
    os.remove(temp)
    return(lines)

def raw_lines():
    lst = []
    n = 0
    again = True
    print """\
----------------------------------------------------------------------
  Enter a note consisting of two or more lines. Begin the first, title 
  line with '+ '. Subsequent lines form the body of the note. 

  Occurrences of !d found anywhere in the note will be replaced with 
  the current date and time. 

  Enter a line containing only '!' to end the note. 
----------------------------------------------------------------------"""
    while again:
        l = raw_input('> ')
        l = l.decode(encoding)
        m = regex_end.match(l)
        if m:
            again = False
        else:
            lst.append(l)
    return(lst)


def get_opts():
    from optparse import OptionParser, OptionGroup
    usage = """usage: %prog [options] [args]"""
    parser = OptionParser(version = "nts %s" % version,
        description = """Manage notes using simple text files. (C) %s Daniel A Graham.""" % copyright, usage=usage)
    args = OptionGroup(parser, "Args", "numbers and ranges of note numbers to display, e.g., '10 14:16' would limit the display to notes numbered 10, 14, 15 and 16.")
    parser.add_option_group(args)
    parser.add_option("-o", action = "store",
        dest='outlineby',  choices = ['p', 't'], default = 'p',
        help = """An element from [p, t] where:	                          \n
        p: outline by path						  \n
        t: outline by tag						  \n
        Default: %default.""")
    parser.add_option("-p", action = "store",
        dest='path',
        help = """Regular expression. Include items with paths matching PATH (ignoring case). Prepend an exclamation mark, i.e., use !PATH rather than PATH, to include items which do NOT have paths matching PATH.""")
    parser.add_option("-t", action = "store",
        dest='tag',
        help = """Regular expression. Include items with tags matching TAG (ignoring case). Prepend an exclamation mark, i.e., use !TAG rather than TAG, to include items which do NOT have tags matching TAG.""")
    parser.add_option("-f", 
        action="store",
        dest='find',
        help = """Regular expression. Include items containing FIND (ignoring case) in the note text. Prepend an exclamation mark, i.e., use !FIND rather than FIND, to include notes which do NOT have note texts matching FIND.""")
    parser.add_option("-d",
        action="store", dest="display", 
        choices = map(str,range(1,8)), default = '1', 
        help="""An integer from [1, ..., 7] which is the sum of one or   \n 
        more of the following:                                           \n
        1: note title                                               \n 
        2: note body                                                \n
        4: note id and tags                                         \n
        Default: %default.""")
    parser.add_option("-l",
        action="store", dest="lines", type=int, default=0,
        help="""If LINES is 0 or if the note body contains no more than LINES + 1 lines, show the entire body of the note. Else show the first LINES lines and append a line showing the number of omitted lines. Default: %default.""")
    parser.add_option("-n",
        action="store", dest="number", 
        choices = ['0','1'], default = '1', 
        help="""0: hide item numbers; 1: Show item numbers.           \n
        Default: %default.""")
    parser.add_option("-e",
        action="store", dest="edit", 
        type=int, 
        help="""If there is a note numbered EDIT among those which satisfy the current filters, then open that note for editing using EDITOR.""")
    parser.add_option("-E",
        action="store", dest="editfile", 
        type=int, 
        help="""If there is a note numbered EDITFILE among those which satisfy the current filters, then open the file containing that note at the beginning line of the note for editing using EDITOR.""")
    parser.add_option("-r",
        action="store", dest="remove", 
        type=int, 
        help="""If there is a note numbered REMOVE among those which satisfy the current filters, then remove that note after prompting for confirmation.""")
    parser.add_option("--tag_usage", action = "store_true",
        dest='tag_usage',
        help = """Print a report showing the number of uses for each tag and exit.""")
    parser.add_option("-a", action = "store_true",
        dest='add',
        help = """Add a new note.""")
    parser.add_option("-q", action = "store_true",
        dest='quick',
        help = """Add a quick note.""")
    parser.add_option("-N", action = "store_true",
        dest='newer',
        help = """Check for a newer version of nts and exit.""")

    (opts, args) = parser.parse_args()
    opts.__dict__['args'] = args
    return(opts.__dict__)

def load_data(hofh = {}):
    global id2note, id2pth, rel2pth, rel2ids, tag2ids, warnings
    id2note, id2pth, rel2pth, rel2ids, tag2ids, hofh = process_data(hofh)
    warnings = log_messages(messages)
    return(hofh)

def log_messages(messages):
    f = os.path.join(ntsexport, 'messages.log')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if messages:
        message = "\n".join(messages)
        ret = """\
%s 
%d files did not load properly. Details were written to:
    %s
%s""" % ("="*60, len(messages),f, "="*60)
    else:
        message = "Currently there are no messages."
        ret = ""
    fo = codecs.open(f, 'w', encoding, 'replace')
    fo.write("%s\nlast modified: %s\n%s\n" % (f,now, "="*30))
    f = fo.write(message)
    fo.close()
    return(ret)

def main():
    global options, filters
    options = get_opts()
    filters = get_filters(options)
    if options['newer']:
        ok, res = get_newer()
        if ok:
            if res:
                msg = res
            else:
                msg = "Version %s of nts is the latest available." % version
        else:
            msg = "The check for latest release of nts failed."
        print "%s\n%s\n%s" % ("="*len(msg), msg, "="*len(msg))
        return()
    if options['quick']:
        get_note(True)
        return()
    if options['add']:
        get_note()
        return()
    load_data()
    if options['tag_usage']:
        print "tag usage report"
        print "%s" % '-'*40
        keys = tag2ids.keys()
        keys.sort()
        for key in keys:
            print "%6d: %s" % (len(tag2ids[key]), key)
        return()
    lofl = make_tree(options, filters)
    if warnings:
        print(warnings)
    print_tree(lofl)

if __name__ == '__main__':
    main()