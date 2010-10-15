#!/usr/bin/env python


import os
import codecs
import poutils

new_po_dir="/home/cillian/Syslab-Reference/Clients/OSHA/translations/"
po_dir="/home/cillian/Syslab/osha/3.3.4/src/Products.OSHATranslations/Products/OSHATranslations/testmerge/"

# Append the new translations to the existing languages
new_pos = os.listdir(new_po_dir)
prefix = "back-to-overview_"
suffix = ".po"
langs = [i.replace(prefix, "").replace(suffix, "") for i in new_pos]

for lang in langs:
    po = codecs.open(po_dir+"osha-"+lang+suffix, "a")
    new_po = codecs.open(new_po_dir+prefix+lang+suffix, "r")
    po.write("\n")
    po.writelines([i.replace("\r\n", "\n") for i in new_po.readlines()])
    po.close()
    new_po.close()

# Copy any duplicate strings to their relevant msgs
# There are often duplications of msgstr values for different msgids,
# Where the msgstrs are the same in the English version the
# corresponding values are duplicated for all other languages, but
# only when the current values are empty or do not already exist.
# e.g. msgids: legend_education, osha_nav_title_education and
# education usually have the same translation
# main_po = poutils.PoSingleFile(po_dir+"osha-en.po")
# dupe_list = main_po.find_duplicate_msgstrs()

# po_files = poutils.PoDirectory(po_dir)
# po_files.copy_duplicate_msgstrs_to_msgids(dupe_list)
