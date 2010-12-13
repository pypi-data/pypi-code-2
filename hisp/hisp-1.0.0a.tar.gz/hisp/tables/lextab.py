# lextab.py. This file automatically created by PLY (version 3.3). Don't edit!
_tabversion   = '3.3'
_lextokens    = {'CLOSER': 1, 'WORD': 1, 'ATTR': 1, 'EXTEND': 1, 'LITERAL': 1, 'MACRO': 1, 'DOCTYPE': 1, 'HTML_COMMENT': 1, 'ELEM': 1, 'CLASS': 1, 'CB': 1, 'VARIABLE': 1, 'ID': 1, 'CP': 1, 'DJANGO_COMMENT': 1, 'BLOCK': 1, 'STRING': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_newline>\\n+)|(?P<t_ignore_COMMENT>\\{!([^}\\\\]|\\\\.)*\\})|(?P<t_HTML_COMMENT>\\(!([^)\\\\]|\\\\.)*\\))|(?P<t_DJANGO_COMMENT>\\{\\#([^}\\\\]|\\\\.)*\\})|(?P<t_DOCTYPE>\\(~([^)\\\\]|\\\\.)*\\))|(?P<t_ATTR>\\(:\\s*[\\w-]+)|(?P<t_MACRO>\\(%\\s*[^\\s{(.#~)}]+)|(?P<t_CLOSER>\\(/\\s*[\\w-]*)|(?P<t_ELEM>\\(\\s*[\\w-]*)|(?P<t_BLOCK>\\{%([^"~}\\\\]|\\\\.|"([^"\\\\]|\\\\.)*")+(?=[~}]))|(?P<t_EXTEND>~)|(?P<t_VARIABLE>\\{([^}\\\\]|\\\\.)*\\})|(?P<t_CP>\\))|(?P<t_CB>\\})|(?P<t_CLASS>(?<!\\s)\\.([\\w-]+))|(?P<t_ID>(?<!\\s)\\#([\\w-]+))|(?P<t_STRING>"([^"\\\\]|\\\\.)*")|(?P<t_LITERAL>\'([^\'\\\\]|\\\\.)*\')|(?P<t_WORD>[^\\s"\\\')}]+)', [None, ('t_newline', 'newline'), ('t_ignore_COMMENT', 'ignore_COMMENT'), None, ('t_HTML_COMMENT', 'HTML_COMMENT'), None, ('t_DJANGO_COMMENT', 'DJANGO_COMMENT'), None, ('t_DOCTYPE', 'DOCTYPE'), None, ('t_ATTR', 'ATTR'), ('t_MACRO', 'MACRO'), ('t_CLOSER', 'CLOSER'), ('t_ELEM', 'ELEM'), ('t_BLOCK', 'BLOCK'), None, None, ('t_EXTEND', 'EXTEND'), ('t_VARIABLE', 'VARIABLE'), None, ('t_CP', 'CP'), ('t_CB', 'CB'), ('t_CLASS', 'CLASS'), None, ('t_ID', 'ID'), None, ('t_STRING', 'STRING'), None, ('t_LITERAL', 'LITERAL'), None, ('t_WORD', 'WORD')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
