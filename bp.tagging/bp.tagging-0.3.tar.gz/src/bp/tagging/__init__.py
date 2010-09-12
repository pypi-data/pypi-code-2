#!/usr/bin/env python2.6
# encoding: utf-8
"""
__init__.py

Created by disko on 2010-08-29.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import cmdln
import mutagen
import sys

from file import File


# CONFIGURATION


# IMPLEMENTATION

class BPTagging(cmdln.Cmdln):
    
    name = "bp_tagging"
    
    def _openFile(self, filename):
        """return a file on which metadata operations can be executed"""
        
        f = File(fname=filename)
        
        if f is None:
            raise ValueError("unsupported filetype - cannot extract metadata")
        
        return f
    
    
    @cmdln.alias("i")
    @cmdln.option("-d", "--debug",   action="store_true", help="print debug information")
    @cmdln.option("-v", "--verbose", action="store_true", help="print extra information")
    def do_info(self, subcmd, opts, *paths):
        """${cmd_name}: print available metadata for files
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        for path in paths:
            try:
                self._openFile(path).pprint()
            except:
                print "no info available on", path
    
    
    @cmdln.alias("rmt")
    @cmdln.option("-d", "--debug",   action="store_true", help="print debug information")
    @cmdln.option("-v", "--verbose", action="store_true", help="print extra information")
    def do_remove_tag(self, subcmd, opts, tag, *paths):
        """${cmd_name}: completely remove TAG from files.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        for path in paths:
            
            try:
                f = self._openFile(path)
            except:
                f = None
            
            if (f is None) or (not f.tags) or (tag not in f.tags):
                continue
            
            f.setTag(tag, "")
            f.save()
            
            if opts.verbose:
                print path
                print " - removed", tag
    
    
    @cmdln.alias("rmtc")
    @cmdln.option("-d", "--debug",   action="store_true", help="print debug information")
    @cmdln.option("-v", "--verbose", action="store_true", help="print extra information")
    def do_remove_tag_with_content(self, subcmd, opts, pattern, *paths):
        """${cmd_name}: remove tags with value PATTERN from files.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        for path in paths:
            if opts.verbose:
                print path
            
            f =self._openFile(path)
            
            if f is not None and f.tags:
                
                for tag in f.tags:
                    if unicode(f.tags[tag]) == unicode(pattern):
                        if opts.verbose:
                            print " - removing", tag
                        f.setTag(tag, "")
                
                f.save()
    
    
    @cmdln.alias("t")
    @cmdln.option("-d", "--debug",   action="store_true", help="print debug information")
    @cmdln.option("-s", "--set",     action="store_true", help="set the tag value")
    @cmdln.option("-v", "--verbose", action="store_true", help="print extra information")
    def do_tag(self, subcmd, opts, tag, value=None, *paths):
        """${cmd_name}: get/set the VALUE for TAG on files.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        if not opts.set:
            paths = [value, ] + list(paths)
            value = None
        
        for path in paths:
            f = self._openFile(path)
            if f is None:
                continue
            
            if opts.verbose:
                print path
            
            if value is None:
                print f.getTag(tag) or "No such tag or empty tag value."
            
            else:
                try:
                    f.setTag(tag, value)
                    f.save()
                    if opts.verbose:
                        print " - set %s to %s" % (tag, value)
                except mutagen.easyid3.EasyID3KeyError, e:
                    msg = [str(e), u"\nValid keys for this file are:\n"]
                    for k in f.valid_keys:
                        msg.append(u" - %s" % k)
                    print msg
    
    
    @cmdln.alias("rpt")
    @cmdln.option("-d", "--debug",   action="store_true", help="print debug information")
    @cmdln.option("-n", "--nosave", action="store_true", help="don't save (only print what would be done).")
    @cmdln.option("-v", "--verbose", action="store_true", help="print extra information")
    def do_replace_in_tag(self, subcmd, opts, tag, pattern, replacement, *paths):
        """${cmd_name}: replace PATTERN with REPLACEMENT in TAG on files. Use 'all' for tag to replace in all tags.
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        if opts.debug:
            print "'info %s' opts:  %s" % (subcmd, opts)
            print "'info %s' paths: %s" % (subcmd, paths)
        
        for path in paths:
            
            f = self._openFile(path)
            
            if f is None:
                continue
            
            if tag == 'all':
                tags = f.tags
            else:
                tags = [tag, ]
            
            if opts.verbose:
                print path
            
            if opts.debug:
                print "tags:", tags
            
            for t in tags:
                old = f.getTag(t)
                
                if old is None:
                    continue
                
                new = old.replace(pattern, replacement)
                
                if old == new:
                    continue
                
                f.setTag(t, new)
                
                if opts.verbose:
                    print " - %s: '%s' => '%s'" % (t, old, new)
            
            if not opts.nosave:
                f.save()
    
    


#def replace_in_tag(filename, tag, pattern, replacement):
#    """replace <pattern> with <replacement> in <tag> for <filename>"""
#    
#    f = _openFile(filename)
#    
#    old = f.getTag(tag)
#    
#    if old is None:
#        print filename, "has no tag", tag
#        return
#    
#    new = old.replace(pattern, replacement)
#    
#    if old == new:
#        return
#    
#    print old, "=>", new
#    f.setTag(tag, new)
#    f.save()
#
#
##@baker.command(shortopts={"overwrite": "o", "split": "s", "tags": "t"})
#def retag_using_filename(filename, tags="artist,title", split=" - ", overwrite=False):
#    """set artist and title tracks from filename
#    
#    :param filename: the file to retag
#    :param tags: comma separated list of tags to set
#    :param split: the filename (without extension) is splitted by <split>. The first item of the resulting sequence will be used as value for the artist tag, the remaining parts will be joined with <split> again and be used as value for the title. (default: " - ")
#    :param overwrite: overwrite existing tags (default: false)
#    """
#    
#    f = _openFile(filename)
#    tags = tags.split(",")
#    
#    for t in tags:
#        if (t in f.tags) and not overwrite:
#            raise baker.CommandError(u"tag <%s> already present. Use -o to overwrite." % t)
#    
#    name_segments = os.path.splitext(os.path.basename(filename))[0].split(split)
#    if len(name_segments) < len(tags):
#        raise baker.CommandError(u"number of filename segments after splitting must be at least the number of tags to set.")
#    
#    tagdict = {}
#    for i in range(len(tags)):
#        if i == len(tags) - 1:
#            # join remaining name segments
#            tagdict[tags[i]] = split.join(name_segments[i:])
#        else:
#            tagdict[tags[i]] = name_segments[i]
#    
#    for tag in tagdict:
#        f.setTag(tag, tagdict[tag])
#    
#    f.save()
#
#
#def tags2filename(filename):
#    """convert the tags to a string suitable for use as a filename"""
#    
#    f = _openFile(filename)
#    print f.filename_from_tags

def main():
    """main entry point"""
    
    bpt = BPTagging()
    sys.exit(bpt.main())



if __name__ == '__main__':
    main()
