#!/usr/bin/env python

import poutils

srcdir = "/home/cillian/Syslab/OSHA/src/Products.OSHATranslations/Products/OSHATranslations/i18n"
ignored_langs = ["ru", "no", "tr", "ja"]
all_msgstrs = [
    "Accident Prevention",
    "Business aspects of OSH",
    "Changing World of Work",
    "Dangerous Substances",
    "Mainstreaming OSH into Education",
    "Musculoskeletal Disorders",
    "Noise",
    "Risk assessment",
    "Stress and psychosocial risks",
    "Workplace Health Promotion",
    "Risk Assessment",
    "Accident Prevention",
    "Health Care Topics",
    "Financial and Economic aspects of OSH",
    "Monitoring of Occupational Safety and Health in the European Union",
    "Cleaning workers",
    ]

pou = poutils.PoDirectory(srcdir, ignored_langs)

print pou.find_all_untranslated(all_msgstrs)
