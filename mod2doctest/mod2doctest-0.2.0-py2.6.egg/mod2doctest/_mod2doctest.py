"""Converts a Python module to a |doctest| testable docstring. 

The basic idea behind |mod2doctest| is provide a *snapshot* of the current
run of a module.  That is, you just point |mod2doctest| to a module and it 
will:

*  Run the module in a interperter.
*  Add all the '>>>' and '...' as needed.
*  Copy all the output from the run and put it under the correct input.
*  Add ellipses where needed like to memory ids and tracebacks. 
*  And provide other formating options. 

This allows you to quickly turn any Python module into a test that you can use
later on to test refactors / regression testing / etc. 

Attributes:

    convert (function): The public interface to |mod2doctest| is the 
    :func:`convert` function.
    
    FLAGS (class): :class:`FLAGS` provides a namespace for all option flags 
    that can be OR'd together to control output. 

    m2d_print (class): :class:`m2d_print` provides a namespace for utility 
    print functions that allow you to print to stdout when running a module 
    but then format nicely for inclusion into the docstring. 
    
    DEFAULT_DOCTEST_FLAGS (int): The default |doctest| flags used when 1) 
    running doctest (if :func:`convert` is directed to run doctest) or 
    when adding the ``if __name__ == '__main__'`` clause to an output
    ``target`` file.  The default options are::

        import doctest
        DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS | 
                                 doctest.REPORT_ONLY_FIRST_FAILURE |
                                 doctest.NORMALIZE_WHITESPACE)
    

"""

import sys
import os
import inspect
import subprocess
import re
import doctest
import time

class FLAGS(object):
    """Option flags used to control docstring output
    
    Option flags include: 

    *  ``ELLIPSE_TRACEBACK`` or ``ET``:  When set, :func:`convert` will replace
       the "middle" part of a traceback with ellipse (the part that contain 
       path references). 
    
    *  ``ELLIPSE_MEM_ID`` or ``EM``:  When set, :func:`convert` will replace
       all memory ids with ellipse (e.g. 0xABCD0120 --> 0x...)

    *  ``ELLIPSE_PATHS`` or ``EP``:  When set, :func:`convert` will replace
       all local paths with ellipse.  For example ``'C:\myfolder\myfile.txt'`` 
       or ``'/usr/myfolder/myfile.txt'`` will go to ``'...myfile.txt'``.  Note, 
       this only works on paths which are within quotes. 

    *  ``REMOVE_NAME_EQUAL_MAIN`` or ``RNM``:  When set, :func:`convert` will 
       remove all content within a ``if __name__ == '__main__':`` block.  This
       allows you to have content within the module without it ending up in 
       the output docstring. 
        
    *  ``COMMENTS TO TEXT`` or ``C2T``:  When set, :func:`convert` will replace
       # comments to be left justified text in the docstring output.     

    *  ``ALL``:  All option flags OR'd together.  
     
    """
    ELLIPSE_TRACEBACK = 1
    ELLIPSE_MEM_ID = 2
    ELLIPSE_PATHS = 4
    COMMENTS_TO_TEXT = 8
    REMOVE_NAME_EQUAL_MAIN = 16
    ET = ELLIPSE_TRACEBACK
    EM = ELLIPSE_MEM_ID
    EP = ELLIPSE_PATHS
    C2T = COMMENTS_TO_TEXT
    RNM = REMOVE_NAME_EQUAL_MAIN
    # ALL THE FLAGS
    ALL = (ET | EM | EP | C2T | RNM)

DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS | 
                         doctest.REPORT_ONLY_FIRST_FAILURE |
                         doctest.NORMALIZE_WHITESPACE)
    
def convert(python_cmd, 
            src=True,
            target=True,
            add_testmod=True,
            flags=FLAGS.ALL,            
            break_on_newlines=True,
            run_doctest=False,
            doctest_flags=DEFAULT_DOCTEST_FLAGS, 
            fn_process_input=None, 
            fn_process_docstr=None, 
            fn_title_docstr=None,             
            ):
    """
    :summary: Runs a module in shell, grabs output and returns a docstring.
    
    :param src: The python module to be converted. If ``True`` is given, the 
                current module is used.  Otherwise, you need to provide 
                either 1) a valid python module object or 2) a path (string)
                to the module to be run. 
    :type src:  True, module or file path
            
    :param target: Where you want the output docstring to be placed.  If: 
                   * ``None``, the docstring is not saved anywhere (but it is 
                   returned by this function).  
                   * ``True`` is given, the src module is used (the 
                   docstring is prepended to the file).  
                   * A path (of type str) is provided, the docstr is saved to 
                   that file.
                   * And finally, a simple convention: if the string '_doctest'
                   is provided, the output is saved to a file with the same
                   name as the input, but with '_doctest' inserted right 
                   before the '.py' of the file name.  For example, if the
                   src filename is 'mytest.py' the output will be saved to 
                   a file called 'mytest_doctest.py'    
    :type target:  None, True, str file path, or str '_doctest'
        
    :param add_testmod: If True a ``if __name__ == '__main__'`` block is added 
                        to the output file IF the ``target`` parameter is an
                        external file (str path). 
    :type add_testmod:  True or False
     
    :param python_cmd: The python command to run to start the shell.
    :type python_cmd:  str
        
    :param flags: A group of OR'd together mod2test flags.  See 
                  :class:`FLAGS` for valid flags. 
    :type flags:  mod2doctest FLAG
    
    :param break_on_newlines: If True, this will convert two or more newlines 
                              in the modules into two newlines in the output
                              docstring.  When False, whitespace is 
                              converted to ``>>>`` in the docstring.  If a 
                              string is provided, two or more newlines are 
                              replaced by the provided string.  
    :type break_on_newlines:  True, False, or str
        
    :param run_doctest: If True doctest is run on the resulting docstring. 
    :type run_doctest:  True or False
            
    :param doctest_flags: Valid OR'd together :mod:`doctest`
                          flags.  The default flags are ``(doctest.ELLIPSIS | 
                          doctest.REPORT_ONLY_FIRST_FAILURE |
                          doctest.NORMALIZE_WHITESPACE)``

    :type doctest_flags: :mod:`doctest` flags
     
    :param fn_process_input: A function that is called and is passed the 
                             module input.  Used for preprocessing.   
    :type fn_process_input:  callable


    :param fn_process_docstr: A function that is called and is passed the 
                              final docstring before saving.  Used for post 
                              processing. You can use this function to perform 
                              your own custom regular expressions 
                              replacements and remove temporal / local data 
                              from your output before |doctest| is run.
    :type fn_process_docstr:  callable

    :param fn_title_docstr: A function that is called and should return a 
                            string that will be used for the title. 
    :type fn_title_docstr:  callable

    :returns: A docstring of type str. 
        
    """

    if src is True:
        src = sys.modules['__main__']
    elif isinstance(src, str):
        if not os.path.isfile(src):
            raise SystemError, "Cannot find src file %s ..." % src
    else:
        raise SystemError, "Unknown src type %s ..." % src

    if inspect.ismodule(src):
        input = open(src.__file__, 'r').read()
    elif isinstance(src, str) and os.path.isfile(src):
        input = open(src, 'r').read()
    elif isinstance(src, str):
        input = src
    else:
        raise SystemError, ("'src' %s must be a valid module or file path, "
                            "or string ...") % obj

    # Remove first docstring ...
    input = _input_remove_docstring(input)

    # Take care of a few minor problems ...
    pinput = _input_fix_whitespace(input)
    pinput = _input_fix_ws_rstrip(pinput)
    pinput = _input_escape_shell_prompt(pinput)       
    pinput = _input_fix_comments(pinput)
    pinput = _input_remove_m2d_print(pinput)
   
    if (flags & FLAGS.REMOVE_NAME_EQUAL_MAIN):
        pinput = _input_remove_name_eq_main(pinput)

    # Remove extra whitespace at end. 
    # You need to do this AFTER the removing of ``if __name__ == '__main__'``
    pinput = '\n\n' + pinput.strip() + '\n'

    shell = subprocess.Popen(args=[python_cmd, "-i"],
                             shell=False,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )

    output = shell.communicate(pinput)[0]

    docstr = _match_input_to_output(pinput, output)
    
    docstr = _docstr_fix_blanklines(docstr)

    docstr = _docstr_fixup(docstr)

    if (flags & FLAGS.ELLIPSE_MEM_ID):
        docstr = _docstr_ellipse_mem_id(docstr)
 
    if (flags & FLAGS.ELLIPSE_PATHS):
        docstr = _docstr_ellipse_paths(docstr)
 
       
    docstr = _docstr_fix_comments(docstr)

    if (flags & FLAGS.ELLIPSE_TRACEBACK):
        docstr = _docstr_ellipse_traceback(docstr)
                 
    if break_on_newlines:
        docstr = _docstr_break_on_newlines(docstr, break_on_newlines)

    docstr = _docstr_left_shift_comments(docstr)
    docstr = _docstr_fixup(docstr)
    if fn_process_docstr:
        docstr = fn_process_docstr(docstr)

    if fn_title_docstr:
        doctitle = fn_title_docstr(docstr)
    else:
        doctitle = _docstr_get_title()

    docstr = '"""%s\n\n%s\n\n"""' % (doctitle, docstr.strip())

    if target:
        
        target = _docstr_save(docstr, src, target, input, add_testmod)
                    
        if run_doctest:
            _run_doctest(target, doctest_flags)

    return docstr

class m2d_print(object):
    """Convenince fns that nicely print to both stdout and docstring output. 
    
    When you run a module, sometimes you want to delimit the output.  
    Therefore, you might use a :func:`print` statement.  However, this will
    cause your output docstring to contain many:: 
    
        >>> print 'foobar'
        foobar 
        
    like statements.  The m2d_print allows you to add the following types of 
    statements to your module::
        
        #=======================================================================
        m2d_print.h1('I AM HERE')
        #=======================================================================
        
    This will print to std out like this:: 

        ========================================================================
        I AM HERE
        ========================================================================

    And will show up in the docstring like this::

        '''
        ========================================================================
        I AM HERE
        ========================================================================
        '''
         
    See :mod:`mod2doctest.tests.m2dprint` for more examples. 

    .. note::
    
       The call:
        
       m2d_print.h1(some_str)

       is the same as:

       m2d_print(some_str)
       
       The latter syntax is provided for convenience. 
       
    """
    
    def __new__(*args, **kwargs):
        return m2d_print.h1(args[1])
                            
    @staticmethod
    def h1(line):
        print '\n\n\n%s\n%s\n%s' %('='*80, line, '='*80)

    @staticmethod
    def h2(line):
        print '\n%s\n%s' % (line, '-'*80)

    @staticmethod
    def h3(line):
        print line
        
    
""" PRIVATE"""    
_ADD_TESTMOD_STR = """
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=%d)
"""
        
_REGEX_INPUT_PROCESS = re.compile(r'''
^\s*            # Start of file, exclude whitespace
(r|R)?          # Allow for raw-strings
"""             # First triple quote.
(.|\n)*?        # Everything in-between, but a non-greedy match   
"""             # Second triple quote.
\s*             # Get rid of all other whitespace.
''', flags=re.VERBOSE)
def _input_remove_docstring(input):
    """Strips the input and removes the first docstring from the input.
    
    .. note;:
    
       The first docstring is never treated as part of the input file.  
       Most notably, because this is when -- if directed -- mod2doctest
       will put the output docstring (at the top of the file). 
    
    """
    input = '\n\n' + _REGEX_INPUT_PROCESS.sub('', input).strip() + '\n'
    return input.replace(r'\r', r'')

def _input_escape_shell_prompt(input):    
    """Replaces `>>>` and '...' with escaped versions."""
    input = input.replace('>>>', '\>>>')
    return input.replace('...', '\...')

_REGEX_INPUT_FIX_COMMENTS = re.compile(r'^(#.*)', flags=re.MULTILINE)
def _input_fix_comments(input):
    """Puts a newline after comments -- needed for post processing."""
    return _REGEX_INPUT_FIX_COMMENTS.sub(r'\1\n', input)

_REGEX_REMOVE_M2D_PRINT = re.compile(r'\nm2d_print.*\([\'"]*(.*?)[\'"]*\).*')
def _input_remove_m2d_print(docstr):
    return _REGEX_REMOVE_M2D_PRINT.sub(r'\n#\1\n', docstr)

_REGEX_INPUT_FIX_WHITESPACE_0 = re.compile(r'(\n[ \t]+)((\n[ \t]*)*)\n')
_REGEX_INPUT_FIX_WHITESPACE_1 = re.compile(r'\n((\n[ \t]+)*)\n')
_REGEX_INPUT_FIX_WHITESPACE_2 = re.compile(r"""(\n[ \t]+.*)
                                            \n(?!else|elif|except|finally)
                                            (\S+.*)""", 
                                            flags=re.VERBOSE)

def _input_fix_whitespace(input):
    """Fixes problems with spaces in the input that cause interpreter errors.

    Normally, a statement like::
    
        def fn()
            print 'foobar'
        for i in range(2):
            print i
    
    will run fine within a module but **not** if pasted into the interpreter.
    
    This module fixes this problem. 
    
    .. note::
    
       This regex makes assumptions about the Python syntax as taken 
       from http://docs.python.org/reference/compound_stmts.html
       
    """
    input = input.replace('\r', '')
    input = _REGEX_INPUT_FIX_WHITESPACE_0.sub(r'\1\n', input)
    input = _REGEX_INPUT_FIX_WHITESPACE_1.sub(r'\n\n', input)
    return _REGEX_INPUT_FIX_WHITESPACE_2.sub(r'\1\n\n\2', input)

_REGEX_INPUT_FIX_WS_RSTRIP = re.compile(r'(\S)[ \t]*\n')
def _input_fix_ws_rstrip(input):
    """Right strips line that contain non whitespace characters."""
    return _REGEX_INPUT_FIX_WS_RSTRIP.sub(r'\1\n', input)
    
_REGEX_NEM = re.compile(r"""
^if\s+__name__\s*==\s*['"]__main__['"]\s*:.*
(\n[ \t].*)*""", flags=re.MULTILINE | re.VERBOSE)
def _input_remove_name_eq_main(input):
    return _REGEX_NEM.sub('', input)

def _match_input_to_output(input, output):
    input = input.replace('\r', '')
    output = output.replace('\r', '')
    docstr = ''
    input = input.split('\n') + ['']
    for line in output.split('\n'):
        docstr = _match_input_to_output_process(docstr, input, line)
    return docstr

def _match_input_to_output_process(docstr, input_lines, output_line):
    started = False
    while True:
        if output_line.startswith('>>> '):
            docstr += '>>> ' + input_lines.pop(0) + '\n'
            started = True
            output_line = output_line[4:]
        elif started and output_line.startswith('... '):
            docstr += '... ' + input_lines.pop(0) + '\n'
            output_line = output_line[4:]
        elif started is True and len(output_line) == 0:
            return docstr
        else:
            return docstr + output_line + '\n'

_REGEX_OUTPUT_FIXUP = re.compile(r'^[ \t]*$', flags=re.MULTILINE)
def _docstr_fix_blanklines(docstr):
    return _REGEX_OUTPUT_FIXUP.sub(r'<BLANKLINE>', docstr)
    
def _docstr_get_title():
    return "\n%s\nAuto generated by mod2doctest on %s\n%s" % \
           ('='*80, time.ctime(), '='*80)

def _docstr_save(docstr, src, target, input, add_testmod):
    
    if inspect.ismodule(src):
        src = src.__file__
    elif not isinstance(src, str):
        raise SystemError, "Unknown src type %s ..." % src

    if target is True:
        target = src
    elif isinstance(target, str):
        if target == '_doctest':
            target = '%s%s.py' % (src.replace('.py', ''), target)
        # Then, if target a string (not True) it is different than the src
        # Therefore, blank out the input so we just get a docstring. 
        input = ''
    else:
        raise SystemError, "Unknown target type %s ..." % target

    if add_testmod and src is not target:
        if add_testmod is True:
            add_testmod  = _ADD_TESTMOD_STR % DEFAULT_DOCTEST_FLAGS
    else:
        add_testmod = ''
            
    output = 'r%s\n%s\n%s' % (docstr,
                              add_testmod,
                              input)
    
    open(target, 'w').write(output)
    
    return target

_REGEX_DOCSTR_FIX_COMMENTS = re.compile(r'(\n>>>\s*#.*)\n... ')
def _docstr_fix_comments(docstr):
    return _REGEX_DOCSTR_FIX_COMMENTS.sub(r'\1', docstr)
           
_REGEX_LEFT_SHIFT_COMMENTS = re.compile(r'^>>>\s*#\s*')
def _docstr_left_shift_comments(docstr):
    count = 0
    in_break = False
    output = ''
    for line in docstr.split('\n'):
        line = line.strip()
        if line == '' and count == 0:
            count += 1
        elif line == '' and count == 1:
            in_break = True
        elif in_break:
            nline = _REGEX_LEFT_SHIFT_COMMENTS.sub(r'', line)
            if line == nline:
                count = 0
                in_break = False
            else:
                line = nline
        output += '\n' + line
    return output
        
_REGEX_THREE_NEWLINES = re.compile(r'\n{2,}')
_REGEX_END_STUFF = re.compile(r'(\n\s*(>>>|<BLANKLINE>)[ |\t]*)*$')
def _docstr_fixup(docstr):
    docstr = docstr.replace(r'"""', r"'''")
    docstr = _REGEX_THREE_NEWLINES.sub(r'\n\n\n', docstr)
    return _REGEX_END_STUFF.sub(r'\n', docstr)
           
_REGEX_NEWLINE_TO_WS = re.compile(r'(\\?>>>\s*\n){2,}')
def _docstr_break_on_newlines(docstr, replace=True):
    if replace is True:
        replace = r'\n\n'
    return _REGEX_NEWLINE_TO_WS.sub(replace, docstr)

_REGEX_ELLIPSE_MEM_ID = re.compile(r'<(?:(?:\w+\.)*)(.*? at 0x)\w+>')
def _docstr_ellipse_mem_id(docstr):
    return _REGEX_ELLIPSE_MEM_ID.sub(r'<...\1...>', docstr)

_REGEX_ELLIPSE_TRACEBACK = re.compile(r"""
                                    (Traceback.*)
                                    (?:(?:\n[ |\t]+.*)*)
                                    (\n\w+.*)
                                    """, flags=re.MULTILINE | re.VERBOSE)
def _docstr_ellipse_traceback(docstr):
    return _REGEX_ELLIPSE_TRACEBACK.sub(r'\1\n    ...\2', docstr)
    
_REGEX_LOCAL_PATH = re.compile(r"""
(\s+['|\"]+)
(?:/+|[a-zA-Z]:\\+)
.*
(?:/+|\\+)
((?:\w|\.)+['|\"]+)
""", flags=re.VERBOSE)
def _docstr_ellipse_paths(output):
    return _REGEX_LOCAL_PATH.sub(r'\1...\2', output)

def _run_doctest(target, doctest_flags):
    doctest.testfile(target, optionflags=doctest_flags)

