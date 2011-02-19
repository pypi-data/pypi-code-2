#!/usr/bin/env python
""" Py2exe setup """

from distutils.core import setup
import py2exe
import glob

setup(
	windows=[
            {
                "script": "ui.py",
                "icon_resources": [(4, "images/sylli.ico")]
                },
            ],
	console=[
            {
                "script": "sylli.py",
                "icon_resources": [(4, "images/sylli.ico")]
                },
            {
                "script": "postinst.py",
                },
            ],
      data_files=[
          	("config", ["config/sonority.txt"]),
            ("config", ["config/sonority_ita-etero.txt"]),
            ("config", ["config/sonority_ita-tauto.txt"]),
		    ("", ["../readme.txt"]),
            ("", ["../changes.txt"]),
		    ("", ["../license.txt"]),
		    ("htmldoc", glob.glob("htmldoc/*.*")),
		    ("images", ["images/sylli.ico"]),
            ("images", ["images/cont.ico"]),
            ("images", ["images/content.png"]),
            ("images", ["images/about.png"])
		]
)
