import codecs
import shutil
import os

import polib

class PoDirectory:
    def __init__(self, srcdir, ignored_langs=[]):
        pofilenames = [i for i in os.listdir(srcdir) if i.endswith(".po")]
        self.pos = []
        for pofile in pofilenames:
            try:
                po = polib.pofile(srcdir+"/"+pofile)
            except IOError, exception:
                import pdb; pdb.set_trace()
                raise Exception(str(exception) + "\n"+ pofile)
            self.pos.append({"pofile":pofile, "po":po})
        # Always ignore 'en' since it is the canonical translation
        self.ignored_langs=ignored_langs+["en"]
        self.langs = self.find_all_langs()

    def find_all_langs(self):
        langs = set()
        for po in self.pos:
            lang = po["po"].metadata["Language-Code"]
            if lang not in self.ignored_langs:
                langs.add(lang)
        return langs

    def copy_duplicate_msgstrs_to_msgids(self, dupe_list):
        for po_dict in self.pos:
            pofile_obj = po_dict["po"]
            pofile_filename = po_dict["pofile"]
            if len(pofile_filename) == 10:
                # let's just stick with osha-xx.po
                for dupe_group in dupe_list:
                    dupe_msgs = []
                    for dupe_msgid in dupe_group:
                        msg_ob = pofile_obj.find(dupe_msgid)
                        if msg_ob:
                            dupe_msgs.append(msg_ob)
                        else:
                            # There isn't already a msg_ob for this
                            # msgid so we create a new one
                            msg_ob = polib.POEntry()
                            msg_ob.msgid = dupe_msgid
                            msg_ob.comment = "Duplicate msgstr"
                            pofile_obj.append(msg_ob)
                            dupe_msgs.append(msg_ob)

                    # Find the value for the msgstr
                    group_msgstr = ""
                    skip_group = False

                    for msg_ob in dupe_msgs:
                        # Check if all the msgstrs match
                        msgstr = msg_ob.msgstr
                        if msgstr:
                            if msgstr == "" or \
                                   group_msgstr and group_msgstr != msgstr:
                                print po_dict["pofile"]
                                print "\n".join(
                                    ["%s: %s" %(i.msgid, i.msgstr) \
                                     for i in dupe_msgs]
                                    )
                                print "enter 1: to use \"%s\", 2: to use \"%s\" or anything else to skip" %(group_msgstr, msgstr)
                                action = raw_input("")
                                if action == "1":
                                    print "Setting all msgstrs to %s" %group_msgstr
                                elif action == "2":
                                    print "Setting all msgstrs to %s" %msgstr
                                    group_msgstr = msgstr
                                else:
                                    print "Skipping"
                                    skip_group = True
                                print "\n"
                                #import pdb; pdb.set_trace()
                            else:
                                group_msgstr = msgstr

                    # Set the same value for all msgs
                    if not skip_group:
                        for msg in dupe_msgs:
                            msg.msgstr = group_msgstr
                pofile_obj.save()

    def find_msgids_by_msgstr(self, msgstr, verbose=False):
        """
        Return all msgids in the canonical "en" po files which
        match the msgstr.
        """
        msgids = []
        for po in self.pos:
            lang = ""
            lang = po["po"].metadata["Language-Code"]
            if lang == "en":
                msg = ""
                msg = po["po"].find(msgstr, "msgstr")
                if msg:
                    msgids.append(msg.msgid)
                    if verbose:
                        print "file:%s \nmsgid:%s \nmsgstr:%s\n\n"\
                              %(po["pofile"], msg.msgid, msg.msgstr)
        return msgids

    def find_msgstrs_by_msgid(self, msgid, verbose=False):
        """
        Return all msgstrs in any language which match a msgid.
        """
        msgs = {}
        for po in self.pos:
            pofile = po["pofile"]
            lang = po["po"].metadata["Language-Code"]
            domain = po["po"].metadata["Domain"]
            msg = po["po"].find(msgid)
            if msg:
                msg_details = {"language":lang,
                               "pofile":pofile,
                               "domain":domain}
                if msgs.has_key(msg.msgstr):
                    msgs[msg.msgstr].append(msg_details)
                else:
                    msgs[msg.msgstr] = [msg_details]
                if verbose:
                    print "lang:\t%s \nfile:\t%s "%(lang, pofile) +\
                          "\nmsgid:\t%s \nmsgstr:\t%s\n"%(msg.msgid, msg.msgstr)
        return msgs

    def find_msgstrs_by_msgstr(self, msgstr, verbose=False, summary=True):
        """
        Return all translated msgs which correspond to an English msgstr.
        A dict is returned with the msgstr as the key and useful
        details as values:

        u'Farlige stoffer': [{'domain': u'osha-navigation',
                              'language': u'da',
                              'pofile': 'osha-navigation-da.po'}],
        """

        msgids = set(self.find_msgids_by_msgstr(msgstr))
        all_msgs = []
        for msgid in msgids:
            msgs = self.find_msgstrs_by_msgid(msgid, verbose)
            if msgs:
                all_msgs.append(msgs)
        return msgs

    def find_untranslated(self, msgstr, verbose=False):
        """
        Return a list of languages which don't include the translation
        for this string.
        """
        msgids = set(self.find_msgids_by_msgstr(msgstr))
        translated_langs = set()
        for msgid in msgids:
            msgs = self.find_msgstrs_by_msgid(msgid, verbose)
            msgstrs = msgs.keys()
            for m in msgstrs:
                # Check that the English version hasn't just been copied
                if m != msgstr:
                    if msgs[m]:
                        # We're interested in any result so we just
                        # look at the first
                        lang = msgs[m][0]["language"]
                        translated_langs.add(lang)
        untranslated_langs = [
            i for i in self.langs if i not in translated_langs
            ]
        if untranslated_langs:
            return {msgstr: untranslated_langs}

    def find_all_untranslated(self, msgstrs = []):
        """
        Given a list of all msgstrs return a list of dictionaries with
        the msgstr as the key and a list of languages without a
        translation as the value:
        {msgstr:["de", "da"]}
        """
        untranslated_msgstrs =  {}
        for msgstr in msgstrs:
            untranslated_msgstr = self.find_untranslated(msgstr)
            if untranslated_msgstr:
                untranslated_msgstrs.update(untranslated_msgstr)
        return untranslated_msgstrs

class PoSingleFile:
    def __init__(self, pofile):
        self.po = polib.pofile(pofile)

    def copy_msgstr_to_comment(self):
        """
        Copy each msgstr into a comment above the msgid in a given po file.
        This is useful for sending an English version for translation.
        """
        for msg in self.po:
            if msg.comment:
                msg.comment = msg.comment + "/n"
            msg.comment = msg.comment + msg.msgstr
        self.po.save()

    def remove_msgs_with_empty_msgstrs(self):
        for msg in self.po:
            if msg.msgstr == "":
                self.po.remove(msg)
        self.po.save()

    def remove_duplicate_msgstrs(self):
        """ Save a copy of the PO file which doesn't contain duplicates """
        fpath = self.po.fpath
        fname,fext = os.path.splitext(fpath)
        no_dupe_path = fname+"_no_duplicates"+fext
        if os.path.exists(no_dupe_path):
            raise Exception("A file named %s already exists." %(no_dupe_path))
        else:
            shutil.copyfile(fpath, no_dupe_path)
            no_dupe_po = polib.pofile(no_dupe_path)
            msgs = set()
            for msg in no_dupe_po:
                if msg.msgstr in msgs:
                    print "Removing duplicate %s" %msg.msgstr
                    no_dupe_po.remove(msg)
                else:
                    msgs.add(msg.msgstr)
            no_dupe_po.save()
            print "PO file without duplicates saved to %s"\
                  %no_dupe_po.fpath

    def find_duplicate_msgstrs(self):
        msgstrs = set()
        dupe_strs = set()
        dupe_list = []

        for msg in self.po:
            if msg.msgstr in msgstrs:
                "%s: %s" %(msg.msgid, msg.msgstr)
                dupe_strs.add(msg.msgstr)
            else:
                msgstrs.add(msg.msgstr)
        for msgstr in dupe_strs:
            msg_group = list()
            for msg in self.po:
                if msg.msgstr == msgstr:
                    msg_group.append(msg.msgid)
            dupe_list.append(msg_group)
        return dupe_list

