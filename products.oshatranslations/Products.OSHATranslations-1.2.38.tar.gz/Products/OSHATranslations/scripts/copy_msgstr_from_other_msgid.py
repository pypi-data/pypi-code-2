import sys
import os

import polib

srcdir = "/home/cillian/Syslab/OSHA/src/Products.OSHATranslations/Products/OSHATranslations/i18n"
srcmsgid = "sme-navdescription_gp_topics"

targetfile = "/home/cillian/Syslab/OSHA/src/Products.OSHATranslations/Products/OSHATranslations/i18n/osha"
targetmsgid = "heading_topics"

pofiles = [i for i in os.listdir(srcdir) if i.endswith(".po")]

for pofile in pofiles:
    try:
        po = polib.pofile(srcdir+"/"+pofile)
    except IOError, exception:
        raise Exception(str(exception) + "\n"+ pofile)
    srcmsg = ""
    srcmsg = po.find(srcmsgid)
    if srcmsg:
        lang = ""
        lang = po.metadata["Language-Code"]
        if lang == "":
            import pdb; pdb.set_trace()
            raise Exception ("No language specified in %s"%pofile)
        target_filename = targetfile+"-"+lang+".po"
        target_po = polib.pofile(target_filename)
        if target_po.find(targetmsgid):
            print "target file: %s\n already has translated this string: %s"\
                  %(target_filename, target_po.find(targetmsgid).msgstr)
        else:
            print "Adding new msgstr: %s for msgid: %s"\
                  % (srcmsg.msgstr, srcmsg.msgid)
            new_entry = polib.POEntry(msgid=targetmsgid, msgstr=srcmsg.msgstr)
            target_po.append(new_entry)
            target_po.save()

# if __name__ == "__main__":
#     dir = sys.argv[1]
#     pofiles = [i for i in os.listdir(dir) if i.endswith(".po")]
