#!/usr/bin/python

"""
Pystaches
=========

A compilation of various Pytache extensions.

## Author and License

Created by [Jonhnny Weslley](http://jonhnnyweslley.net).

Contact: jw [at] jonhnnyweslley.net

Copyright 2010 Jonhnny Weslley

License: MIT License (see LICENSE for details)
"""

class SyntaxHighlighter:

  tab_length = 2
  linenos = False
  prefix='highlight_'
  css_class = "highlight"

  def __getattr__(self, name):
    if name.startswith(self.prefix):
      lang = name[len(self.prefix):]
      return lambda code: self._highlight(lang,code)
    raise AttributeError, name

  def _highlight(self, lang, code):
    try:
      from pygments import highlight
      from pygments.formatters import HtmlFormatter
      from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    except ImportError:
      # just escape and pass through
      txt = self._escape(code)
      if self.linenos:
        txt = self._number(txt)
      else :
        txt = '<div class="%s"><pre>%s</pre></div>\n' % (self.css_class, txt)
      return txt
    else:
      try:
        lexer = get_lexer_by_name(lang)
      except ValueError:
        try:
          lexer = guess_lexer(code)
        except ValueError:
          lexer = TextLexer()
      formatter = HtmlFormatter(linenos=self.linenos, cssclass=self.css_class)
      return highlight(code, lexer, formatter)

  def _escape(self, txt):
    """ basic html escaping """
    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt

  def _number(self, txt):
    """ Use <ol> for line numbering """
    # Fix Whitespace
    txt = txt.replace('\t', ' '*self.tab_length)
    txt = txt.replace(" "*4, "&nbsp; &nbsp; ")
    txt = txt.replace(" "*3, "&nbsp; &nbsp;")
    txt = txt.replace(" "*2, "&nbsp; ")        

    # Add line numbers
    lines = txt.splitlines()
    txt = '<div class="codehilite"><pre><ol>\n'
    for line in lines:
      txt += '\t<li>%s</li>\n'% line
    txt += '</ol></pre></div>\n'
    return txt


class EmbedVideo:

  def google_video(self, video_id):
    return "<embed id=\"VideoPlayback\" src=\"http://video.google.com/googleplayer.swf?docid=%s\" style=\"width:400px;height:326px\" allowFullScreen=\"true\" allowScriptAccess=\"always\" type=\"application/x-shockwave-flash\"></embed>" % video_id

  def youtube(self, video_id):
    return "<object width=\"480\" height=\"385\"><param name=\"movie\" value=\"http://www.youtube.com/v/%s\"></param><param name=\"allowFullScreen\" value=\"true\"></param><param name=\"allowscriptaccess\" value=\"always\"></param><embed src=\"http://www.youtube.com/v/%s\" type=\"application/x-shockwave-flash\" allowscriptaccess=\"always\" allowfullscreen=\"true\" width=\"480\" height=\"385\"></embed></object>" % (video_id, video_id)

  def vimeo(self, video_id):
    return "<iframe src=\"http://player.vimeo.com/video/%s\" width=\"400\" height=\"225\" frameborder=\"0\"></iframe>" % video_id

