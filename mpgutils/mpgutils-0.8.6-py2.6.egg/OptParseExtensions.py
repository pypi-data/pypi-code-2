'''
Created on Jul 7, 2009

@author: nemesh
'''

from optparse import IndentedHelpFormatter
import textwrap  
import string

class IndentedHelpFormatterWithNL(IndentedHelpFormatter):
  """This class is blatantly stolen from some usenet help found at
  http://groups.google.com/group/comp.lang.python/browse_thread/thread/6df6e6b541a15bc2/09f28e26af0699b1?pli=1
  The desire here is to allow newlines into your help string in optparse, so you can do some programatic formatting"""
  
  def format_description(self, description):
    if not description: return ""
    desc_width = self.width - self.current_indent
    indent = " "*self.current_indent
# the above is still the same
    bits = description.split('\n')
    formatted_bits = [
      textwrap.fill(bit,
        desc_width,
        initial_indent=indent,
        subsequent_indent=indent)
      for bit in bits]
    result = "\n".join(formatted_bits) + "\n"
    return result

  def format_option(self, option):
    # The help for each option consists of two parts:
    #   * the opt strings and metavars
    #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
    #   * the user-supplied help string
    #   eg. ("turn on expert mode", "read data from FILENAME")
    #
    # If possible, we write both of these on the same line:
    #   -x    turn on expert mode
    #
    # But if the opt string list is too long, we put the help
    # string on a second line, indented to the same column it would
    # start in if it fit on the first line.
    #   -fFILENAME, --file=FILENAME
    #       read data from FILENAME
    result = []
    opts = self.option_strings[option]
    opt_width = self.help_position - self.current_indent - 2
    if len(opts) > opt_width:
      opts = "%*s%s\n" % (self.current_indent, "", opts)
      indent_first = self.help_position
    else: # start help on same line as opts
      opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
      indent_first = 0
    result.append(opts)
    if option.help:
      help_text = self.expand_default(option)
# Everything is the same up through here
      help_lines = []
      for para in help_text.split("\n"):
        table = ''.join(' ' if (n < 32 or n > 126) and n!=10 else chr(n) for n in xrange(256))
        para=string.translate(para, table)  
        t= textwrap.wrap(para, self.help_width)
        #t=[string.translate(i,table) for i in t]
        help_lines.extend(t)
# Everything is the same after here
      result.append("%*s%s\n" % (
        indent_first, "", help_lines[0]))
      result.extend(["%*s%s\n" % (self.help_position, "", line)
        for line in help_lines[1:]])
    elif opts[-1] != "\n":
      result.append("\n")
    return "".join(result) 
