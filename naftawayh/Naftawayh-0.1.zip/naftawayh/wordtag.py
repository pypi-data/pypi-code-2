#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
Arabic Word Tagger:
This class can identify the type of word (noun, verb, prepostion).
"""
import tashaphyne
from stopwords import *
from specialwords import *

import re
import string
import sys
from arabic_const import *
from ar_ctype import *

from affix_const import *
from verb_stamp import *

#STAMP_pat=re.compile(u"[%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s]"%(ALEF,YEH,HAMZA,ALEF_HAMZA_ABOVE,WAW_HAMZA,YEH_HAMZA,  WAW, ALEF_MAKSURA,SHADDA,FATHA,DAMMA,KASRA,SUKUN,TEH,NOON),re.UNICODE)
#STAMP_pat=re.compile(u"[%s%s%s%s]"%(ALEF,YEH, WAW, ALEF_MAKSURA),re.UNICODE)
STAMP_pat=re.compile(u"[%s]"%u''.join([ALEF,YEH,HAMZA,ALEF_HAMZA_ABOVE,WAW_HAMZA,YEH_HAMZA,  WAW, ALEF_MAKSURA,SHADDA,FATHA,DAMMA,KASRA,SUKUN,TEH,NOON]),re.UNICODE)
def verb_stamp(word):
	"""
	generate a stamp for a verb,
	remove all letters which can change form in the word :
	-ALEF,
	-HAMZA,
	-YEH,
	-WAW,
	-ALEF_MAKSURA
	-SHADDA
	@return:
	"""
	# strip the last letter if is doubled
	if word[-1:]== word[-2:-1]:
		word=word[:-1];
	return STAMP_pat.sub('',word)
class WordTagger():
	"""
	Arabic Word tagger
	"""
	def __init__(self,):
		self.word=u"";
		self.verbstemmer=tashaphyne.ArabicLightStemmer();
		# prepare the verb stemmer
		verb_prefix=u"أسفلونيتا"
		verb_infix=u"اتوي"
		#verb_suffix=u"امتكنهوي"
		verb_suffix=u"امكهناوت"		
		verb_max_prefix=4
		verb_max_suffix=6
		self.VERB_STAMP=VERB_STAMP;
		self.verbstemmer.set_max_prefix_length(verb_max_prefix);
		self.verbstemmer.set_max_suffix_length(verb_max_suffix);
		self.verbstemmer.set_prefix_letters(verb_prefix);
		self.verbstemmer.set_suffix_letters(verb_suffix);
		self.verbstemmer.set_prefix_list(VERBAL_PREFIX_LIST);
		self.verbstemmer.set_suffix_list(VERBAL_SUFFIX_LIST);
		self.verbstemmer.infix_letters=verb_infix;
		# prepare the noun stemmer
		self.nounstemmer=tashaphyne.ArabicLightStemmer();
		# the noun prefixes here are the gramatical affixes
		# and not the inflectionel affixes, for this  porpus, you don't find the MEEM, TEH etc.
		noun_prefix=u"أفالكوب"		
		noun_infix=u"اتوي"
		noun_suffix=u"امتةكنهوي"
		noun_max_prefix=4
		noun_max_suffix=6

		self.nounstemmer.set_max_prefix_length(noun_max_prefix);
		self.nounstemmer.set_max_suffix_length(noun_max_suffix);
		self.nounstemmer.set_prefix_letters(noun_prefix);
		self.nounstemmer.set_suffix_letters(noun_suffix);SUFFIXES_LIST
		self.nounstemmer.set_prefix_list(NOMINAL_GRAMMATICAL_PREFIXES_LIST);
		self.nounstemmer.set_suffix_list(SUFFIXES_LIST);		
		self.nounstemmer.infix_letters=noun_infix;
		#self.create_verb_stamp_dictionary()

	def create_verb_stamp_dictionary(self):
		"""
		A private ffunction to load verrb dictionary and create a special index of verb stamps
		"""	
		for verb in VERB_DICTIONARY.keys():
			#self.verbstemmer.lightStem(verb);
			# want to enhance the stamp work with the stemming the original verb
#			stem=self.verbstemmer.get_stem()
#			stamp=self.verb_stamp(stem);
			stamp=self.verb_stamp(verb);
			if stamp in self.VERB_STAMP.keys():
				self.VERB_STAMP[stamp].append(verb);
			else:
				self.VERB_STAMP[stamp]=[verb];
			#print "VERB_STAMP={";
			#for stamp in self.VERB_STAMP.keys():
			#	print (u"u'%s':[u'%s'],"%( stamp,"', u'".join(VERB_STAMP[stamp]))).encode('utf8');
			#print "}";

	def is_noun(self,word):
		"""
		Return True if the word is a possible noun form
		@param word: word.
		@type word: unicode.
		@return: is a noun or not
		@rtype: Boolean
		"""
		if self.is_possible_noun(word)>=0:
			return True;
		else:
			return False;

	def is_verb(self,word):
		"""
		Return True if the word is a possible verb form

		@param word: word.
		@type word: unicode.
		@return: is a noun or not
		@rtype: Boolean
		"""

		if self.is_possible_verb(word)>=0:
			return True;
		else:
			return False;
	def lightStemming(self,word):
		"""
		Stem the word as verb and noun, it be prepared for tagging
		This function has no return;
		@param word: word.
		@type word: unicode.
		"""
		#stem the word as a verb
		# ajust Alef_madda to double alef_hamza above
		word=re.sub(ur"[%s]"%ALEF_MADDA,ALEF_HAMZA_ABOVE*2,word);
		self.verbstemmer.lightStem(word);
		self.nounstemmer.lightStem(word);

	def is_possible_noun(self,word):
		"""
		Return True if the word is a possible noun form
		This function return True, if the word is valid, else, return False

		@param word: word.
		@type word: unicode.
		@return: error code : indicate the id of the rules aplied. Negative, if not a verb
		@rtype: integer
		"""


		#stem the word as a verb
		#self.verbstemmer.lightStem(word);
		starword=self.verbstemmer.get_starword();
		word_nm=self.verbstemmer.get_unvocalized();
		guessed_word=self.guess_stem(word_nm)
		verbstem=self.verbstemmer.get_stem();
		verbsuffix=self.verbstemmer.get_suffix();		
		verbprefix=self.verbstemmer.get_prefix();			
		verbstarstem=self.verbstemmer.get_starstem();		

		#self.nounstemmer.lightStem(word);
		nounstarstem=self.nounstemmer.get_starstem();
		nounprefix=self.nounstemmer.get_prefix();
		nounsuffix=self.nounstemmer.get_suffix();
		nounstem=self.nounstemmer.get_stem();		

		if len(verbstem)>5:
			#print "\t".join([word,verbstem]).encode('utf8');
			return 150;
	# HAMZA BELOW ALEF
		if re.search(ur"[%s%s%s%s%s]"%(ALEF_HAMZA_BELOW,TEH_MARBUTA,FATHATAN,DAMMATAN,KASRATAN),word):
			 return 100;

		elif re.search(ur"[%s](.)+"%ALEF_MAKSURA,word):
			 return 120;			
	# the prefix has alef lam, and the starstem has 3 stars
	#is a noun and not a verb
		if re.search(ur"[%s%s]%s"%(ALEF,LAM,LAM),nounprefix) and (nounstarstem.count('*')>=3 or nounstarstem.find(u'*%s*'%ALEF)>=0):
			return 170;

		# if the stemmed word starts and ens by stars, and the lenght is greater than 4 letters, is a noun
		if len(verbstem)>=5 and  verbstarstem.startswith('*') and re.search(ur"[^%s%s%s%s%s]$"%(ALEF,YEH,TEH,ALEF_HAMZA_ABOVE,NOON),verbprefix) and verbstarstem.endswith('*'):
			return 141;
		# if len(word)>=5 and starword.startswith('*') and starword.endswith('*'):
			# return 140;
		# search the stem stamp in the verb stamp, if not existe then , is a noun
		# the stamp is a psedou root
		if not self.is_valid_verb_stamp(verbstem):
			return 160;

	# the word is started by Noon, before REH or LAM, or Noon, is a verb and not a noun
		if verbprefix.endswith(NOON) and re.match(ur"^[%s%s%s]"%(REH,LAM,NOON),verbstem):
		#if re.match(ur"^%s[%s%s%s]"%(NOON,REH,LAM,NOON),word_nm):

			return -10;		

	# the word is started by YEH,
	# before some letters is a verb and not a noun
		#ToDo: expect some cases
		if verbprefix.endswith(YEH) and re.match(ur"^[%s]"%u''.join([YEH,THAL,JEEM,HAH,KHAH,ZAIN,SHEEN,SAD,DAD,TAH,ZAH,GHAIN,KAF,YEH]),verbstem) and len(verbstem)>=2:
			return -20;
		#predecated
		if re.match(ur"^%s[%s%s%s%s%s%s%s%s%s%s%s%s%s]"%(YEH,THAL,JEEM,HAH,KHAH,ZAIN,SHEEN,SAD,DAD,TAH,ZAH,GHAIN,KAF,YEH),word_nm):
			return -21;


	# To redo
	#the word is like ift3l pattern
		# if re.search(ur"[%s%s%s%s%s]\*%s\*\*"%(ALEF,YEH,NOON,TEH,ALEF_HAMZA_ABOVE,TEH),starword):

			# return -30;
	# the word is like inf3l pattern
		if re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"%s\*\*\*"%NOON,verbstarstem):
			return -41;
		if not re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"%s%s\*\*\*"%(ALEF,NOON),verbstarstem):
			return -42;			
	# the word is like ift3l pattern			
		if re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"\*%s\*\*"%TEH,verbstarstem):
			return -44;
		if not re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"%s\*%s\*\*"%(ALEF,TEH),verbstarstem):
			return -45;			
		if  re.search(ur"[%s%s%s%s%s]%s\*\*\*"%(ALEF,YEH,NOON,TEH,ALEF_HAMZA_ABOVE,NOON),starword):

			return -40;
			
	# the word is like isf3l pattern
		if re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"%s%s\*\*\*"%(SEEN,TEH),verbstarstem):
			return -51;	
		if not re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and re.search(ur"%s%s%s\*\*\*"%(ALEF,SEEN,TEH),verbstem):
			return -52;				
		if re.search(ur"[%s%s%s%s%s]%s%s([^%s%s%s]{2})([^%s%s%s%s])"%(ALEF,YEH,NOON,TEH,ALEF_HAMZA_ABOVE,SEEN,TEH,ALEF,YEH,WAW,ALEF,HEH,KAF,NOON),word_nm):
			return -50;
	# the word contains y|t|A)st*
	# يست، أست، نست، تست
		# duplicated, same as 51
		# if re.search(ur"(%s|%s|%s|%s)%s%s\*"%(ALEF_HAMZA_ABOVE,YEH,TEH,NOON,SEEN,TEH),starword) :

			# return -60;
	# the word contains ist***
	# استفعل
		#duplicated as 52
		# if re.search(ur"%s%s%s\*\*\*"%(ALEF,SEEN,TEH),starword) :

			# return -70;

	# the word contains ***t when **+t+* t is TEH
	# if TEH is followed by meem, alef, noon
	# تم، تما، تن، تا، تني
	# حالة تنا غير مدرجة
	# تا تعطي مشكلة مع باكستاني وموريتاني
		if re.search(ur"تم|تما|تن|تني",verbsuffix) and verbstarstem.count("*")>=3 :
			return -81;
		# if re.search(ur"\*\*\*%s(%s|%s|%s[^%s])"%(TEH,MEEM,ALEF,NOON,ALEF),starword) :
			# return -80;


	#To reDo
	### case of ***w  w is waw, this case is a verb,
	### the case of ***w* is a noun
	##	if re.search(u"\*\*\*%s[^\*%s]"%(WAW,NOON),starword):
	##		if starword.count("*")==3:
	##
	##		  return -90;
	##		else:
	##		  if re.search(u"\*\*\*\*%s%s"%(WAW,ALEF),starword):
	##			return -100;

	# case of future verb with waw noon,
	#same as the verb rule 1105
		if (verbsuffix.startswith(WAW+NOON) or verbsuffix.startswith(ALEF+NOON)) and (verbprefix.endswith(YEH) or verbprefix.endswith(TEH)) and len(verbstem)>=2 and len(verbstem)<6:
			return -111;	
		# if re.search(u"^([^\*%s])*[%s%s](.)*\*\*\*%s%s"%(MEEM,YEH,TEH,WAW,NOON),starword):
			# return -110;
	# case of future verb with ALEf noon,
	#same as the verb rule 1105	
		# if re.search(u"^([^\*%s])*[%s%s](.)*\*\*\*%s%s"%(MEEM,YEH,TEH,ALEF,NOON),starword):
			# return -115;

	# case of yt,tt,nt and 3 stars is a verb like yt*** or yt*a**
	# at is an ambiguous case with hamza of interogation.
		if re.search(ur"[%s%s%s%s]$"%(ALEF_HAMZA_ABOVE,YEH,NOON,TEH),verbprefix) and verbstem.startswith(TEH) and verbstarstem.count("*")>=3:
			return -121;
		# if re.search(u"^([^\*])*[%s%s%s]%s(\*\*\*|\*%s\*\*)"%(YEH,TEH,NOON, TEH,ALEF),starword):
			# return -122;
	# case of yn,tn,nn and 3 stars is a verb like yn*** or yn*a* or ynt**
		#same as 41
		# if re.search(u"^([^\*])*[%s%s%s]%s(\*\*\*|\*%s\*|%s\*\*)"%(YEH,TEH,NOON,NOON,ALEF,TEH),starword):

			# return -130;
	# case of y***, y
	# exception ; case of y**w*
		if verbprefix.endswith(YEH) and verbstarstem.count('*')>=3 and re.search(u"(\*\*\*|\*%s\*\*)"%ALEF,verbstarstem):
			return -141;		
		# if re.search(u"^([^\*])*%s(\*\*\*|\*%s\*\*)"%(YEH,ALEF),starword):
			# return -140;
# To do
# لا تعمل مع كلمة البرنامج
##	# the word contains a****  a is alef is a verb
##		if re.search(ur"^([^\*])*%s(\*\*\*\*)"%(ALEF),starword) :
##
##			return -150;
	# the word ends with wa  a is WAW alef , is a verb
		if verbsuffix.endswith(WAW+ALEF):
			return -161;	
		# if re.search(ur"([^%s%s%s]..)%s%s$"%(ALEF_HAMZA_ABOVE, WAW,FEH,WAW,ALEF),starword) :
			# return -160;
	# the word has suffix TM (TEH MEEM)  and two original letters at list, is a verb
		#duplicated, same as 81
		# if re.search(u"%s%s([^\*])*$"%(TEH,MEEM),starword) and starword.count("*")>=2 :

			# return -170;
	# the word ends with an added TEH
		#exception and problem: whre the teh marbuta is opened
		# if verbsuffix.startswith(TEH) and re.search(u"[%s]$"%u''.join([THEH,JEEM,DAL,THAL,ZAIN,SHEEN,TAH,ZAH]),verbstem):
			# return -181;
		if re.search(u"-%s$"%(TEH),guessed_word):
			return -180;
	# the word starts with  an added YEH
		if verbprefix.endswith(YEH) and re.search(u"^[%s]"%u''.join([THEH,JEEM,HAH,KHAH,THAL,ZAIN,SHEEN,SAD,DAD,TAH,ZAH,GHAIN,KAF,HEH,YEH]),verbstem):
			return -191;
		# if re.search(u"^%s-"%(YEH),guessed_word):
			# return -190;

		return 0;

	#---------------------------------------
	def is_possible_verb(self,word):
		"""
		Return True if the word is a possible verb form
		This function return True, if the word is valid, else, return False
		A word is not valid verb if :
		  - minimal lenght : 3
		  - starts with ALEF_MAKSURA, WAW_HAMZA,YEH_HAMZA,
			HARAKAT
		  - contains : TEH_MARBUTA
		  - contains  ALEF_MAKSURA at the began or middle.
		  - contains : double haraka : a warning
		  - contains : ALEF_HAMZA_BELOW
		  - contains: tanween
		@param word: word.
		@type word: unicode.
		@return: error code : indicate the id of the rules aplied. Negative, if not a verb
		@rtype: integer


		"""

		#self.nounstemmer.lightStem(word);
		starword=self.nounstemmer.get_starword();
		word_nm=self.nounstemmer.get_unvocalized();
		nounstarstem=self.nounstemmer.get_starstem();
		nounstem=self.nounstemmer.get_stem();		
		nounprefix=self.nounstemmer.get_prefix();
		nounsuffix=self.nounstemmer.get_suffix();		

		#self.verbstemmer.lightStem(word);
		verbstem=self.verbstemmer.get_stem();
		verbstarstem=self.verbstemmer.get_starstem();		
		verbprefix=self.verbstemmer.get_prefix();
		verbsuffix=self.verbstemmer.get_suffix();

		# The word is not valid 
		# the ALEF MAKSURA can't be at the middle 
		if re.search(ur"[%s](.)+"%ALEF_MAKSURA,word):
			return -1020;
		# Marks and some letters can't be at the begining
		if re.search(ur"^[%s]"%u''.join([WAW_HAMZA,YEH_HAMZA,FATHA,DAMMA,SUKUN,KASRA]),word):			return -1000;

	# the prefix has alef lam, and the starstem has 3 stars
	#is a noun and not a verb
		if re.search(ur"[%s%s]%s$"%(ALEF,LAM,LAM),nounprefix) and nounstarstem.count('*')>=3:
			return -1310;
		if re.search(ur"[%s%s]%s$"%(ALEF,LAM,LAM),nounprefix) and nounstarstem.find(u'*%s*'%ALEF)>=0:
			return -1320;
		# search the stem stamp in the verb stamp, if not existe then , is a noun
		# the stamp is a psedou root
		if not self.is_valid_verb_stamp(verbstem):
			return -1300;


	#The case of present tense in arabic
	# where the prefix contains YEH or TEH, and the suffix starts with ALEF+NOON, or WAW NOON.
	# exception:
	# words like يابانيون، ييمنيون، يساريون،
		if (verbsuffix.startswith(WAW+NOON) or verbsuffix.startswith(ALEF+NOON)) and (verbprefix.endswith(YEH) or verbprefix.endswith(TEH)) and len(verbstem)>=2 and len(verbstem)<6:
			return 1105;
			
	# HAMZA BELOW ALEF
		elif re.search(ur"[%s%s%s%s%s]"%(ALEF_HAMZA_BELOW,TEH_MARBUTA,FATHATAN,DAMMATAN,KASRATAN),word):
			return -1010;


	# the word is like ift3al pattern
		elif re.match(ur"%s([^%s%s%s%s%s]%s|[%s%s%s]%s|[%s]%s)(.)%s(.)"%(ALEF,LAM,SEEN,SAD,DAD,ZAH,TEH,SAD,DAD,ZAH,TAH,ZAIN,DAL,ALEF),nounstem):
			return -1030;	

		# the word is like inf3al pattern
		elif re.match(ur"%s%s(..)%s(.)"%(ALEF,NOON,ALEF),nounstem):

			return -1040;			


	# the word is like istf3al pattern
		elif re.match(ur"%s%s%s(..)%s(.)"%(ALEF,SEEN,TEH,ALEF),nounstem):
			return -1050;


	# the word is finished by HAMZA preceded by ALEF
	#and more than 2 originals letters
		elif re.match(ur"\*\*%s%s"%(ALEF,HAMZA),nounstarstem):
			return -1060;

	# the word contains three ALEF,
	# the last ALEF musn't be at end, in the verb
		if re.match(ur"^(.)*([%s](.)+){3}$"%(ALEF),word_nm):

			return -1070;

	# the word is started by beh, before BEH,FEH,MEEM
	#is a noun and not a verb
		if nounprefix.endswith(BEH) and re.match(ur"^[%s%s%s]"%(BEH,FEH,MEEM),nounstem):
			return -1080;	

	# the word is started by meem, before BEH,FEH,MEEM
	#is a noun and not a verb
		if re.match(ur"^%s[%s%s%s]"%(MEEM,BEH,FEH,MEEM),nounstem):
			return -1090;

	# case of meem has three original letters in follwoing
		if re.search(u"^([^\*])*%s"%(MEEM),nounstarstem) and nounstarstem.count('*')>=3:
			return -1140;
	# case of meem folowed by t, noon, st, has two original letters in folloing
		if re.search(u"^([^\*])*%s(%s|%s|%s%s)"%(MEEM,TEH,NOON,SEEN,TEH),nounstarstem) and nounstarstem.count('*')>=2:
			return -1145;


	# the word is finished by ALEF TEH
	# and the  original letters are more than two,

		if re.search(ur"%s%s"%(ALEF,TEH),nounsuffix) and nounstarstem.count('*')>=3:
			return -1150;

	# the word contains **Y* when y is Yeh
		if re.search(ur"\*\*%s\*"%(YEH),nounstarstem) :
			return -1160;
	# the word contains al*Y* when ALEF-LAM+*+yeh+*is Yeh
		#if re.search(ur"%s%s\*%s\*"%(ALEF,LAM,YEH),starword) :
		if (nounprefix.endswith(ALEF+LAM)or nounprefix.endswith(LAM+LAM) ) and re.search(ur"\*%s\*"%YEH,nounstarstem) and  nounstarstem.count('*')>=2:
			return -1170;

	# the word contains alw and at least two stars ** when ALEF-LAM+WAW+*  w is Waw
		if (nounprefix.endswith(ALEF+LAM)or nounprefix.endswith(LAM+LAM) or nounstem.startswith(MEEM)) and re.search(WAW,nounstarstem) and  nounstarstem.count('*')>=2:
			return -1180;


	# the word contains ***w* when ***+WAW+* w is Waw
		if re.search(ur"[^%s]\*\*%s\*"%(u"تاينلفأو",WAW),nounstarstem) :

			return -1190;
	# the word contains **a* when **+a+* a is alef
		if re.search(ur"\*[\*%s]%s\*"%(u"وي",ALEF),nounstarstem) :

			return -1200;
	# the word contains t**y* when **+t+* a is alef
		if re.search(ur"%s\*\*%s\*"%(TEH,YEH),nounstarstem) :
			return -1210;
	# case of word ends  with ALEf noon, if it hasnt Yeh or teh on prefix
		if verbsuffix.startswith(ALEF+NOON) and verbstarstem.count("*")>=2 and not (verbprefix.endswith(YEH) or verbprefix.endswith(TEH)) :
			return -1220;	
		return 0;

	def guess_stem(self,word):
		"""
		Detetect affixed letters based or phonetic root composition.
		In Arabic language, there are some letters which can't be adjacent in a root.
		This function return True, if the word is valid, else, return False

		@param word: the word.
		@type word: unicode.
		@return: word with a '-' to indicate the stemming position.
		@rtype: unicode
		"""
	# certain roots are forbiden in arabic
	#exprimed in letters sequences
	# but this sequence can be used for affixation
	#then we can guess that this letters are affixed
	#
	#treat one prefixe letter
	# we strip harkat and shadda
		word=ar_strip_marks(word);
		prefixes_letters=(TEH, MEEM,LAM,WAW,BEH, KAF,FEH,HAMZA,YEH,NOON)
		prefixes_forbiden={
		ALEF_HAMZA_ABOVE:(ALEF_HAMZA_ABOVE,ZAH,AIN,GHAIN),
		BEH:(BEH,FEH,MEEM),
		TEH:(THEH,DAL,THAL,ZAIN,SHEEN,SAD,DAD,TAH,ZAH),
		FEH:(BEH,FEH,MEEM),
		KAF:(JEEM,DAD,TAH,ZAH,QAF,KAF),
		LAM:(REH,SHEEN,LAM,NOON),
		MEEM:(BEH,FEH,MEEM),
		NOON:(REH,LAM,NOON),
		WAW:(WAW,YEH),
		YEH:(THEH,JEEM,HAH,KHAH,THAL,ZAIN,SHEEN,SAD,DAD,TAH,ZAH,GHAIN,KAF,HEH,YEH),
			}

		word_guess=word;
		if len(word)>=2:
			c1=word[0];
			c2=word[1];
#			if c1 in prefixes_letters and (c1 in prefixes_forbiden.keys() and c2 in prefixes_forbiden[c1]):
			if  prefixes_forbiden.has_key(c1) and c2 in prefixes_forbiden[c1]:

				word_guess=u"%s-%s"%(c1,word[1:])
				if len(word_guess)>=4:
					c1=word_guess[2];
					c2=word_guess[3];
					if c1 in prefixes_letters and ( c2 in prefixes_forbiden[c1]):
						word_guess=u"%s-%s"%(c1,word_guess[2:])




	# treat two suffixe letters
		bisuffixes_letters=(KAF+MEEM,KAF+NOON,HEH+MEEM,HEH+NOON)

		bisuffixes_forbiden={
		HEH+MEEM:(ALEF_HAMZA_ABOVE,HAMZA,WAW_HAMZA,YEH_HAMZA,BEH,THEH,HAH, KHAH, SAD, DAD, TAH,ZAH,AIN,GHAIN,HEH,YEH),
		KAF+MEEM:(ALEF_HAMZA_ABOVE,HAMZA,WAW_HAMZA,YEH_HAMZA,BEH,THEH,JEEM, KHAH,ZAIN,SEEN, SHEEN,DAD, TAH,ZAH,GHAIN, FEH, QAF,KAF, LAM, NOON, HEH,YEH),
		HEH+NOON:(ALEF_HAMZA_ABOVE,HAMZA,WAW_HAMZA,YEH_HAMZA,BEH,THEH,JEEM,HAH, KHAH, SAD, DAD, TAH,ZAH,AIN,GHAIN,HEH,YEH),
		KAF+NOON:(ALEF_HAMZA_ABOVE,HAMZA,WAW_HAMZA,YEH_HAMZA,BEH,THEH,JEEM,HAH, KHAH,THAL,SHEEN,DAD, TAH,ZAH,AIN, GHAIN, QAF,KAF, NOON, HEH,YEH),

			}
	##	word_guess=word;
		word=word_guess;
		if len(word)>=3:
			bc_last=word[-2:];
			bc_blast=word[-3:-2]
			if bc_last in bisuffixes_letters:
				if bc_blast in bisuffixes_forbiden[bc_last]:
					word_guess=u"%s-%s"%(word[:-2],bc_last)

	# treat one suffixe letters
		suffixes_letters=(KAF,TEH,HEH)

		suffixes_forbiden={
		TEH:(THEH,JEEM,DAL,THAL,ZAIN,SHEEN,TAH,ZAH),
		KAF:(THEH,JEEM,KHAH, THAL,TAH,ZAH,GHAIN,QAF),
		HEH:(TEH,HAH,KHAH,DAL,REH,SEEN,SHEEN,SAD,ZAH,AIN,GHAIN),
			}
		word=word_guess;
		c_last=word[-1:];
		c_blast=word[-2:-1]
		if c_last in suffixes_letters:
			if c_blast in suffixes_forbiden[c_last]:
				word_guess=u"%s-%s"%(word[:-1],c_last)


		return word_guess;


	def is_valid_stem(self,stem):
		"""
		Return True if the stem is valid.
		A stem can't be started by SHADDA, WAW_HAMZA, YEH_HAMZA.
		@param stem: the stem.
		@type stem: unicode.
		@return: is valid a stem.
		@rtype: Boolean
		"""

		if stem[0] in (WAW_HAMZA,YEH_HAMZA,SHADDA):
			return False;
		stem_guessed=guess_stem(stem);
		if re.search("-",stem_guessed):
			return False;
		return True;


	def context_analyse(self,word_one, word_two,tag1='nv',tag2='nv'):
		"""
		Detect the word type according to the previous word.
		@param word_one: the previous word.
		@type word_one: unicode.
		@param word_two: the word to detect.
		@type word_two: unicode.

		@return: a code of word type ('v': verb, 'vn': verb& noun, 'n': noun)
		@rtype: unicode
		"""

		tab_noun_context=(
		u"في",
		u"بأن",
		u"بين",
		u"ففي",
		u"وفي",
		u"عن",
		u"إلى",
		u"على",
		u"بعض",
		u"تجاه",
		u"تلقاء",
		u"جميع",
		u"حسب",
		u"سبحان",
		u"سوى",
		u"شبه",
		u"غير",
		u"كل",
		u"لعمر",
		u"مثل",
		u"مع",
		u"معاذ",
		u"نحو",
		u"خلف",
		u"أمام",
		u"فوق",
		u"تحت",
		u"يمين",
		u"شمال",
		u"دون",
		u"من",
		u"بدون",
		u"خلال",
		u"أثناء",
		)
		tab_verb_context=(
		u"قد",
		u"فقد",
		u"وقد",
		u"لن",
		u"لم",
		)
		if word_one in tab_verb_context: return "v";
		elif word_one in tab_noun_context: return "n";
		elif word_two in tab_noun_context or word_two in tab_noun_context:
			return "t";
		# إذا تلا الاسم كلمة تبدأ بألف لام
		elif word_two.startswith(ALEF+LAM) and tag1=='n':
			return 'n';
		return "vn";

	def verb_stamp(self,word):
		"""
		generate a stamp for a verb,
		remove all letters which can change form in the word :

		"""

		return verb_stamp(word)

	def is_valid_verb_stamp(self,verb):
		"""
		Return True if the verb stamp exists in the dictionary index of verb stamps
		@param verb: the verb.
		@type verb: unicode.

		@return: True if exists, False, else.
		@rtype: Boolean
		"""
		if self.VERB_STAMP.has_key(self.verb_stamp(verb)) :
			return True;
		else:
			return False;

	def is_stopword(self,word):
		"""
		Return True if the word is a stopword, according a predefined list.
		@param word: the previous word.
		@type word: unicode.

		@return: is the word a stop word
		@rtype: Boolean
		"""
		if  STOPWORDS.has_key(word):
			return True;
		else:
			return False;
	def is_specialword(self,word):
		"""
		Return True if the word is a special,liek a verb form word used as noun
		as youcef يوسف, yathrib يثرب, yazid يزيد, according a predefined list.
		@param word: the word.
		@type word: unicode.

		@return: is the word a secial word.
		@rtype: Boolean
		"""
		if SPECIALWORDS.has_key(word):
			return SPECIALWORDS[word];
		else:
			return False;
