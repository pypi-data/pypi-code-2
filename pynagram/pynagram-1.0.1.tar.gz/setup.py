#! /usr/bin/python
# 
#     setup.py
# 
#     Copyright (c) 2009, 2010, 2011 Umang Varma <umang.me@gmail.com>.
# 
#     This file is part of Pynagram
# 
#     Pynagram is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Pynagram is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Pynagram. If not, see <http://www.gnu.org/licenses/>.
#
from distutils.core import setup
import glob
#import py2exe

r = setup(name= "pynagram",
        version= "1.0.1",
        description= "Pynagram - Unjumble the letters and get addicted!",
        author= "Umang Varma",
        author_email= "umang.me@gmail.com",
        url= "https://launchpad.net/pynagram",
        packages= ["pynagram", "pynagram.gui", "pynagram.backend"],
        scripts= ["bin/pynagram"],
        data_files= [("share/pynagram", glob.glob("wordlist/*"))],
        windows= [{"script": "bin/pynagram", "icon_resources": [(1, "icons/pynagram.ico")]}],
        options={"py2exe": {"skip_archive": False, "includes": ["sip"]}},
        license="GPLv3",
        long_description="""anagram word game
Pynagram is a simple word game in which the player is presented with seven
letters in a random order. Every word that is "solved" from the jumbled letters
earns the player points. If the player solves one or more seven letter words,
the score is carried over into the next game.

Pynagram was inspired from Anagramarama."""
        )
