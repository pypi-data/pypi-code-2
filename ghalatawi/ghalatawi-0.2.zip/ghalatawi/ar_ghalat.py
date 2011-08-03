#!/usr/bin/python
# -*- coding=utf-8 -*-
#************************************************************************
# $Id: ar_ghalat.py,v 0.7 2011/01/05 01:10:00 Taha Zerrouki $
#
# ------------
# Description:
# ------------
#  Copyright (c) 2011, Arabtechies, Arabeyes Taha Zerrouki
#
#  Elementary function to detect and correct minor spell error for  arabic texte
#
# -----------------
# Revision Details:    (Updated by Revision Control System)
# -----------------
#  $Date: 2011/01/05 01:10:00 $
#  $Author: Taha Zerrouki $
#  $Revision: 0.2 $
#  $Source: ghalatawi.sourceforge.net
#
#  This program is written under the GPL License.
#
#***********************************************************************/
"""
Ghalatawi: Arabic AutoCorrection module
@author: Taha Zerrouki
@contact: taha dot zerrouki at gmail dot com
@copyright: Arabtechies, Arabeyes,  Taha Zerrouki
@license: GPL
@date:2011/01/05
@version: 0.2
"""
import re
import pyarabic.araby as araby
"""
@var ArabicAutocorrectWordlist: Common error on stop words.
@var ReplacementTable: Table of regular expression to be treated.
"""
ArabicAutocorrectWordlist={
#common error on stop words
u'اذا':u'إذا',
u'او':u'أو',
u'فى':u'في',
u'هى':u'هي',
u'انت':u'أنت',
u'انتما':u'أنتما',
u'الى':u'إلى',
u'التى':u'التي',
u'الذى':u'الذي',
}



ReplacementTable=[
# removing kashida (Tatweel)
#(re.compile(ur'([\u0621-\u063F\u0641-\u064A])\u0640+([\u0621-\u063F\u0641-\u064A])',re.UNICODE), ur'\1\2'), 
# rules for انفعال
(re.compile(ur'\b(و|ف|)(ك|ب|)(ال|)إن(\w\w)ا(\w)(ي|)(ين|ات|ة|تين|)\b',re.UNICODE), ur'\1\2\3ان\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)(لل|)إن(\w\w)ا(\w)(ي|)(ين|ات|تين|ة|)\b',re.UNICODE), ur'\1\2ان\3ا\4\5\6'),
(re.compile(ur'\b(و|ف|)(ك|ب|ل|)إن(\w\w)ا(\w)(ي|)(هما|كما|هم|كم|هن|كن|نا|ه|ك|ها|تهما|تكما|تهم|تكم|تهن|تكن|تنا|ته|تها|تك|اتهما|اتكما|اتهم|اتكم|اتهن|اتكن|اتنا|اته|اتها|اتك|)\b',re.UNICODE), ur'\1\2ان\3ا\4\5\6'),
(re.compile(ur'\b(و|ف|)(ال|)إن(\w\w)ا(\w)(ي|)(ين|ان|تين|تان|ون|)\b',re.UNICODE), ur'\1\2ان\3ا\4\5\6'),
(re.compile(ur'\b(و|ف|)إن(\w\w)ا(\w)(ي|)(ًا|اً|ا|)\b',re.UNICODE), ur'\1ان\2ا\3\4\5'),
# rules for افتعال
(re.compile(ur'\b(و|ف|)(ك|ب|)(ال|)إ(\w)ت(\w)ا(\w)(ي|)(ين|ات|ة|تين|)\b',re.UNICODE), ur'\1\2\3ا\4ت\5ا\6\7\8'),
(re.compile(ur'\b(و|ف|)(لل|)إ(\w)ت(\w)ا(\w)(ي|)(ين|ات|تين|ة|)\b',re.UNICODE), ur'\1\2ا\3ت\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)(ك|ب|ل|)إ(\w)ت(\w)ا(\w)(ي|)(هما|كما|هم|كم|هن|كن|نا|ه|ك|ها|تهما|تكما|تهم|تكم|تهن|تكن|تنا|ته|تها|تك|اتهما|اتكما|اتهم|اتكم|اتهن|اتكن|اتنا|اته|اتها|اتك|)\b',re.UNICODE), ur'\1\2ا\3ت\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)(ال|)إ(\w)ت(\w)ا(\w)(ي|)(ين|ان|تين|تان|ون|)\b',re.UNICODE), ur'\1\2ا\3ت\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)إ(\w)ت(\w)ا(\w)(ي|)(ًا|اً|ا|)\b',re.UNICODE), ur'\1ا\2ت\3ا\4\5\6'),
# rules for افتعال التي تحوي ضط أو صط أو زد
(re.compile(ur'\b(و|ف|)(ك|ب|)(ال|)إ(زد|ضط|صط)(\w)ا(\w)(ي|)(ين|ات|ة|تين|)\b',re.UNICODE), ur'\1\2\3ا\4\5ا\6\7\8'),
(re.compile(ur'\b(و|ف|)(لل|)إ(ﺯﺩ|ﺾﻃ|ﺺﻃ)(\w)ا(\w)(ي|)(ين|ات|تين|ة|)\b',re.UNICODE), ur'\1\2ا\3\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)(ك|ب|ل|)إ(ﺯﺩ|ﺾﻃ|ﺺﻃ)(\w)ا(\w)(ي|)(هما|كما|هم|كم|هن|كن|نا|ه|ك|ها|تهما|تكما|تهم|تكم|تهن|تكن|تنا|ته|تها|تك|اتهما|اتكما|اتهم|اتكم|اتهن|اتكن|اتنا|اته|اتها|اتك|)\b',re.UNICODE), ur'\1\2ا\3\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)(ال|)إ(ﺯﺩ|ﺾﻃ|ﺺﻃ)(\w)ا(\w)(ي|)(ين|ان|تين|تان|ون|)\b',re.UNICODE), ur'\1\2ا\3\4ا\5\6\7'),
(re.compile(ur'\b(و|ف|)إ(ﺯﺩ|ﺾﻃ|ﺺﻃ)(\w)ا(\w)(ي|)(ًا|اً|ا|)\b',re.UNICODE), ur'\1ا\2\3ا\4\5\6'),
# حالة الألف المقصورة بعدها همزة في آخر الكلمة، وعادة مايكون البديل همزة على النبرة. 
(re.compile(ur'ىء\b',re.UNICODE), ur'ئ'),
# حالة الألف المقصورة ليست في آخر الكلمة، وعادة مايوضع بعدها فراغ 
(re.compile(ur'ى([^ء]+)\b',re.UNICODE), ur'ى \1'),
# حالة التاء المربوطة ليست في آخر الكلمة، وعادة مايوضع بعدها فراغ 
(re.compile(ur'ة(\w+)\b',re.UNICODE), ur'ة \1'),
# حالة الالف المكررة بعدها لام،يكون البديل بين اﻷلفين فراغ
#(re.compile(ur'\bاال(\w+)\b',re.UNICODE), ur'ال\1'),
#(re.compile(ur'(\w+)اال(\w+)\b',re.UNICODE), ur'\1ا ال\2'),
#(re.compile(ur'(\w+)(ا+)(\w+)\b',re.UNICODE), ur'\1ا\3'),
#(re.compile(ur'ا(ا+)',re.UNICODE), ur'ا'),
]

def isArabicword(word):
    """ Checks for a valid Arabic word.
    An Arabic word not contains spaces, digits and pounctuation
    avoid some spelling error,  TEH_MARBUTA must be at the end.
    @param word: input word
    @type word: unicode
    @return: True if all charaters are in Arabic block
    @rtype: Boolean
    """
    return araby.isArabicword(word);

def autocorrectByRegex(word):
	"""
	Autocorrect by using regular expression from remplacement table.
	
	Example:
		>>> word=u"الإجتماعية"
		>>> autocorrectByRegex(word)
		 الاجتماعية
	
	@param word: the input word.
	@type word: unicode.
	@return: corrected word, if the word is common error, or False.
	@rtype: unicode or False.
	"""
	# autocorrect words without diacritics 
	word=araby.stripTatweel(word);
	word_nm=araby.stripTashkeel(word)
	for rule in ReplacementTable:
		# rule[0]: pattern
		# rule[1]: replacement  
		result=rule[0].sub(rule[1],word_nm);
		# if the result changes, return True;
		if result!=word_nm:
			return result;
	#if all rules don't match, return False;
	return False;
def autocorrectByWordlist(word,wordlist=ArabicAutocorrectWordlist):
	"""
	Autocorrect by using word list.
	the default list is ArabicAutocorrectWordlist.
	
	Example:
		>>> autocorrectlist={
			u'اذا':u'إذا',
			u'او':u'أو',
			u'فى':u'في',
			u'هى':u'هي',
			u'انت':u'أنت',
			u'انتما':u'أنتما',
			u'الى':u'إلى',
			u'التى':u'التي',
			u'الذى':u'الذي',
			}
		>>> word=u"اذا"
		>>> autocorrectByWordlist(word, autocorrectlist)
		 إذا
	
	@param word: the input word.
	@type word: unicode.
	@return: corrected word, if the word is common error, or False.
	@rtype: unicode or False.
	"""
	# autocorrect words from a list 
	# autocorrect words without diacritics
	word=araby.stripTatweel(word);
	word_nm=araby.stripTashkeel(word)
	if ArabicAutocorrectWordlist.has_key(word):
		return ArabicAutocorrectWordlist[word];
	else: 
		return False;
def loadAutocorrectWordlistFromFile(myfile):
	"""
	Load Autocorrect list from a file, to the global list autocorrect_arabic_list.
	
	Example:
		>>> autocorrectlist=loadAutocorrectWordlistFromFile("data/arabic.acl")
		>>> word=u"اذا"
		>>> autocorrectByWordlist(word, autocorrectlist)
		 إذا
	
	@param myfile: the input word.
	@type myfile: unicode.
	@return: wordlist, if loaded, else False.
	@rtype: Boolean.
	"""
	# load autolist from file
	try:
		fl=open(myfile);
	except:
		# file not found
		return False;
	line=fl.readline().decode("utf8");
	nb_field=2;
	dWordlist={}
	while line :
		line=line.strip("\n");
		if not line.startswith("#"):
			liste=line.split("\t");
			if len(liste)>=nb_field:
				#error=liste[0];
				#correct=liste[1];
				dWordlist[liste[0]]=liste[1];
		line=fl.readline().decode("utf8");
	fl.close();
	return dWordlist;





