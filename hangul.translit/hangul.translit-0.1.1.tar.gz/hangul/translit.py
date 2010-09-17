# -*- coding:utf8 -*-

ur"""
Date: 2010-9-16

Transliterate Hangul(Korean) to alphabet according to Revised Romanization of Korean(2000)

Usage:
    >>> from hangul import translit
    >>> translit.test()
    한국                    --> han-guk
    한국어                  --> han-gugeo
    저작권                  --> cheojakkweon
    저작                   --> cheojak
    작심삼일                 --> chaksimsamil
    밧줄                   --> patchul
    
    >>> s = translit.romanize('한국어')
    >>> print s
    han-gugeo
    >>>
    >>> s = translit.romanize('안녕하세요!')
    >>> print s
    annyeonghaseyo!

Reference Sites:
    http://en.wikipedia.org/wiki/Revised_Romanization_of_Korean
    http://ko.wikipedia.org/wiki/국어의_로마자_표기법
    http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html
    http://code.google.com/p/krtpy/
    http://unicode.org/reports/tr15/#Hangul
    http://jrgraphix.net/research/unicode_blocks.php?block=90
"""

__version__ = '0.1.1'
__author__ = 'Lee Sun-yeon <lee_soonyeon@gmail.com>'



import re

# 처믕 또는 마지막 음절인지 검사하기 위해 사용됨 
whitespace = re.compile('\s')

# HANGUL COMPATIBILITY JAMO
# They can be write at isolation.
# From 0x3164 to 0x318E are not written in modern Hangul so I truncated it.
ISOLATED_JAMO_RANGE = [0x3131, 0x3136]  
ISOLATED_JAMO_TABLE = [
'g', 'kk', 'gs', 'n', 'nj', 'nh', 'd', 'tt', 'l', 'lg', 'lm', 'lb', 'ls', 'lt', 'lp',
'lh', 'm', 'b', 'pp', 'ps', 's', 'ss', 'j', 'jj', 'ch', 'k', 't', 'p', 'h', 'a',
'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'wo', 
'we', 'wi', 'yu', 'eu', 'ui', 'i'
]

# HANGUL JAMO
LEAD_BASE = 0x1100      # lead consonant, choseong: 초성 
VOWEL_BASE = 0x1161     # medial vowel, chungseong:중성 
TAIL_BASE = 0x11A7      # tail consonant, chongseong:종성 
SYLLABLE_BASE = 0xAC00  # syllable, 44032 
VOWEL_RANGE = [VOWEL_BASE, 0x1175]

LEAD_COUNT = 19
VOWEL_COUNT = 21
TAIL_COUNT = 28
N_COUNT = VOWEL_COUNT * TAIL_COUNT      # 588
SYLLABLE_COUNT = LEAD_COUNT * N_COUNT   # 11172

JAMO_LEAD_TABLE  = ['g', 'gg', 'n', 'd', 'dd', 'r', 'm', 'b', 'bb', 's', 'ss', '', 'j', 'jj', 'c', 'k', 't', 'p', 'h']
JAMO_VOWEL_TABLE = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'weo', 'we', 'wi', 'yu', 'eu', 'yi', 'i']
JAMO_TAIL_TABLE  = ['', 'g', 'gg', 'gs', 'n', 'nj', 'nh', 'd', 'l', 'lg', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh', 'm', 'b', 'bs', 's', 'ss', 'ng', 'j', 'c', 'k', 't', 'p', 'h']


# Constants and Tables for consonant transcribe
CONSONANT_LEAD = [0x110B, 0x1100, 0x1102, 0x1103, 0x1105, 0x1106, 0x1107, 0x1109, 
                  0x110C, 0x110E, 0x110F, 0x1110, 0x1111, 0x1112,'word_final']
CONSONANT_TAIL = [0x11A8, 0x11AB, 0x11AF, 0x11B7, 0x11B8, 0x11BC, 0x11BA,'any_vowel','initial']
CONSONANT_TRANSCRIBE_TABLE = [
    # (tail) ㄱ/G  ㄴ/N  ㄹ/L  ㅁ/M  ㅂ/B  ㅇ/NG  ㅅ/S  any_vowel  initial
    ['g', 'n', 'r', 'm', 'b', 'ng', 's', '', ''],                               # (lead) ㅇ /- 
    ['kk', 'n-g', 'lg', 'mg', 'pk', 'ngg', 'tk', 'g', 'k'],                     # ㄱ /G
    ['ngn', 'nn', 'll', 'mn', 'mn', 'ngn', 'nn', 'n', 'n'],                     # ㄴ /N
    ['kt', 'nd', 'lt', 'md', 'pt', 'ngd', 'tt', 'd', 't'],                      # ㄷ /D
    ['ngn', 'll', 'll', 'mn', 'mn', 'ngn', 'sl', 'r', 'r'],                     # ㄹ /R
    ['ngm', 'nm', 'lm', 'mm', 'mm', 'ngm', 'nm', 'm', 'm'],                     # ㅁ /M
    ['kp', 'nb', 'lb', 'mb', 'pp', 'ngb', 'tp', 'b', 'p'],                      # ㅂ /B
    ['ks', 'ns', 'ls', 'ms', 'ps', 'ngs', 'ts', 's', 's'],                      # ㅅ /S
    ['kch', 'nj', 'lch', 'mj', 'pch', 'ngj', 'tch', 'j', 'ch'],                 # ㅈ /J
    ['kch-', 'nch-', 'lch-', 'mch-', 'pch-', 'ngch-', 'sch-', 'ch-', 'ch-'],    # ㅊ /C
    ['kk-', 'nk-', 'lk-', 'mk-', 'pk-', 'ngk-', 'sk-', 'k-', 'k-'],             # ㅋ /K
    ['kt-', 'nt-', 'lt-', 'mt-', 'pt-', 'ngt-', 'st-', 't-', 't'],              # ㅌ /T
    ['kp-', 'np-', 'lp-', 'mp-', 'pp-', 'ngp-', 'sp-', 'p-', 'p-'],             # ㅍ /P
    ['kh', 'nh', 'rh', 'mh', 'ph', 'ngh', 'th', 'h', 'h'],                      # ㅎ /H
    ['k', 'n', 'l', 'm', 'p', 'ng', 't', '', '']                                # word final
]

def decompose(s):
    code_point = ord(s)
    if code_point in xrange(ISOLATED_JAMO_RANGE[0], ISOLATED_JAMO_RANGE[1]+1):
        return s
    
    index = code_point - SYLLABLE_BASE
    if index not in xrange(0, SYLLABLE_COUNT):
        return unichr(index)
    
    initial = LEAD_BASE + index / N_COUNT
    vowel = VOWEL_BASE + (index % N_COUNT) / TAIL_COUNT
    final = TAIL_BASE + index % TAIL_COUNT
    if final == TAIL_BASE:
        final = None
        return ', '.join((unichr(initial), unichr(vowel)))
    return ', '.join((unichr(initial), unichr(vowel), unichr(final)))
    
def romanize(raw, from_enc='utf8', to_enc='utf8'):   
    if from_enc != None:
        raw = raw.decode(from_enc)
     
    new_string = []
    last_tail_code_point = None

    for i in range(len(raw)):
        code_point = ord(raw[i])
        if code_point in xrange(ISOLATED_JAMO_RANGE[0], ISOLATED_JAMO_RANGE[1]+1):
            new_string.append( ISOLATED_JAMO_TABLE[code_point - ISOLATED_JAMO_RANGE[0]] )
            last_tail_code_point = None
            continue
        
        index = code_point - SYLLABLE_BASE
        if index not in xrange(0, SYLLABLE_COUNT):
            new_string.append( unichr(code_point) )
            last_tail_code_point = None
            continue
        
        lead_idx = index / N_COUNT
        vowel_idx = (index % N_COUNT) / TAIL_COUNT
        tail_idx = index % TAIL_COUNT
        
        lead = JAMO_LEAD_TABLE[lead_idx]
        vowel = JAMO_VOWEL_TABLE[vowel_idx]
        tail = JAMO_TAIL_TABLE[tail_idx]
        
        # Transcribes certain phonetic changes that occur with 
        # combinations of the final consonant
        # of one character and the initial consonant of the next,
        
        # Set current letter's code point
        lead_code_point = LEAD_BASE + lead_idx
        tail_code_point = TAIL_BASE + tail_idx
    
        if lead_code_point in CONSONANT_LEAD:
            transcribe_table_lead_idx = CONSONANT_LEAD.index(lead_code_point)
            transcribe_table_tail_idx = None
       
            # last tail is consonant
            if last_tail_code_point in CONSONANT_TAIL:
                transcribe_table_tail_idx = CONSONANT_TAIL.index(last_tail_code_point)
                del(new_string[len(new_string) - 1][-1:])
            
            # last tail is vowel
            #elif last_tail_code_point in xrange(VOWEL_RANGE[0], VOWEL_RANGE[1]+1):
            elif last_tail_code_point and last_tail_code_point - TAIL_BASE  == 0:
                transcribe_table_tail_idx = CONSONANT_TAIL.index('any_vowel')
                
            # lead is initial
            elif i == 0 or (i > 0 and whitespace.match(raw[i-1]) ):
                transcribe_table_tail_idx = CONSONANT_TAIL.index('initial')  
            
            if transcribe_table_tail_idx is not None:
                lead = CONSONANT_TRANSCRIBE_TABLE[transcribe_table_lead_idx][transcribe_table_tail_idx]       
             
        # 막지막 음절이면 음절의 종성을 테이블표에 따라 교체한다.
        if tail_code_point in CONSONANT_TAIL and \
        (i == len(raw) - 1 or (i != (len(raw) - 1) and whitespace.match(raw[i+1]) )):
            l_idx = CONSONANT_LEAD.index('word_final')
            t_idx = CONSONANT_TAIL.index(tail_code_point)
            tail = CONSONANT_TRANSCRIBE_TABLE[l_idx][t_idx]
        
        last_tail_code_point = TAIL_BASE + tail_idx
        if tail:
            new_string.append( [lead, vowel, tail] )
        else:
            new_string.append( [lead, vowel] )

    return ''.join(map(lambda x: ''.join(x), new_string)).encode(to_enc)

def test():   
    tests = ['한국', '한국어', '저작권', '저작', '작심삼일', '밧줄', '안녕하세요!']
    #tests = [u'작심삼일']
    
    for s in tests:
        print "% -20s --> %s" % (s, romanize(s))
    
if __name__ == '__main__':
    print "Testing"
    test()    
    
    