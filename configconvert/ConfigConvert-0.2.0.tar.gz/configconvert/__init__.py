"""\
ConfigConvert is a set of ConversionKit converters designed specifically to
help you create Python objects from options set in a text file.
"""

import getopt
import logging
import os

log = logging.getLogger(__name__)

from configconvert.internal import eval_import, simple_import, import_module
from bn import uniform_path as up, AttributeDict
from nestedrecord import decodeNestedRecord, encode_error
from conversionkit import Conversion

#
# ConversionKit handlers
#

def stringToObject():
    """\
    Takes a string written in the format ``"path.to.module:object"`` and 
    returns the object.
    """
    def stringToObject_converter(conversion, state):
        value = conversion.value
        try:
            result = eval_import(value)
        except ImportError, e:
            conversion.error = (
                'Could not import object %r specified in the config '
                'file. The error was %s'
            )%(value, str(e))
        else:
            conversion.result = result
    return stringToObject_converter

# XXX Quick hack.
unicodeToObject=stringToObject

#
# File Handling Converters
#    

def existingDirectory(
    try_to_create=False, 
    raise_on_create_error=False,
    uniform_path=False,
    include_value_in_error=True,
):
    """\
    Ensure the directory specified as the input exists and is not a file, 
    otherwise set an error.

    If ``try_to_create`` is ``True``, the converter will try to create the
    directory if it doesn't exist. In that case you can set
    ``raise_on_create_error`` to ``True`` to have any problems creating the
    directory trigger an exception instead of setting a conversion error.

    If the directory exists (or has been created) the directory path is set
    as the conversion result. If ``uniform_path`` is set to ``True``, the 
    absolute, normalized path is set instead of the value given as the input.
    """
    def existingDirectory_converter(conversion, state):
        directory = conversion.value
        if not os.path.exists(directory):
            if try_to_create:
                # Try to create it
                try:
                    os.mkdir(directory)
                except:
                    if raise_on_create_error:
                        raise
                    if include_value_in_error:
                        conversion.error = 'Could not create the directory %r' % (
                            directory
                        )
                    else:
                        conversion.error = 'Could not create the directory'
                else:
                    if uniform_path:
                        conversion.result = up(directory)
                    else:
                        conversion.result = directory
            else:
                if include_value_in_error:
                    conversion.error = 'The directory %r doesn\'t exist'%directory
                else:
                    conversion.error = 'The directory doesn\'t exist'
        elif not os.path.isdir(directory):
            if include_value_in_error:
                conversion.error = 'The path %r is not a directory'%directory
            else:
                conversion.error = 'The path is not a directory'
        else:
            if uniform_path:
                conversion.result = up(directory)
            else:
                conversion.result = directory
    return existingDirectory_converter

def existingFile(
    try_to_create=False, 
    raise_on_create_error=False, 
    file_content='',
    uniform_path=False,
    include_value_in_error=True,
):
    """\
    Ensure the file specified as the input exists and is not a directory, 
    otherwise set an error.

    If ``try_to_create`` is ``True``, the converter will try to create the file
    if it doesn't exist with the content ``file_content`` which defaults to `''``.
    The file is opened with mode ``'wb'`` (write binary) so the contents of
    ``file_content`` should be a binary string in the encoding you wish to use. If
    the content is an ordinary Python string, that is fine. If it is a Unicode
    string you'll need to encode it to an appropriate format first. For example: 

    ::

        existingFile(try_to_create=True, file_content=unicode_string.encode('utf8'))

    If you have set ``try_to_create`` to ``True`` you can set
    ``raise_on_create_error`` to ``True`` so that any problems which are encountered
    when creating the file trigger an exception instead of setting a conversion error.

    If the file exists (or has been created) the file path is set as the conversion
    result. If ``uniform_path`` is set to ``True``, the 
    absolute, normalized path is set instead of the value given as the input.
    """
    def existingFile_converter(conversion, state):
        filename = conversion.value
        if not os.path.exists(filename):
            if try_to_create:
                # Try to create it
                try:
                    fp = open(filename, 'wb')
                    fp.write(file_content)
                    fp.close()
                except:
                    if raise_on_create_error:
                        raise
                    if include_value_in_error:
                        conversion.error = 'Could not create the file %r' % (
                            filename
                        )
                    else:
                        conversion.error = 'Could not create the file'
                else:
                    if uniform_path:
                        conversion.result = up(filename)
                    else:
                        conversion.result = filename
            else:
                if include_value_in_error:
                    conversion.error = 'The file %r doesn\'t exist'%filename
                else:
                    conversion.error = 'The file doesn\'t exist'
        elif os.path.isdir(filename):
            if include_value_in_error:
                conversion.error = 'The path %r is not a file'%filename
            else:
                conversion.error = 'The path is not a file'
        else:
            if uniform_path:
                conversion.result = up(filename)
            else:
                conversion.result = filename
    return existingFile_converter

# This isn't a post-converter and I'm not sure where it would be used
##
## Post-converters
##
#
#def attribute_dict(conversion, state):
#    # No point in importing it unless it is needed
#    from powerpack.util import AttributeDict
#    conversion.result = AttributeDict(conversion.value)

#
# Parse Config
#

def parse_config(filename, encoding='utf8'):
    r"""\
    Parse a config file with a strict format.

    The config file is made of options and values which are each defined on a
    single line terminated by a ``\n`` character and separtated by only the 
    three characters *space equals space*. For example:

    ::

        option = value

    The parsed config file results in a dictionary with the options as ASCII
    strings for the keys and the values as unicode strings for the values. The
    options must start with the letters a-z, A-Z or _ and should contain only
    letters, numbers or the ``_`` character. Thus the option values have the
    same naming rules as Python variables.

    If you don't leave a space each side of the ``=`` character it is
    considered a syntax error. Any extra space characters after the space
    after the equals sign are treated as part of the value. For example this:

    ::

        option =  value
   
    would result in the option ``'option'`` taking the value ``u' value'``. 
    Any extra spaces after the option name are ignored though.

    The file must use UNIX style line endings (ie each line ends in ``\n``)
    and must be encoded as UTF-8. Values can therefore take any Unicode
    character as long as the file is encoded correctly.

    You can also specify multiline values. You do so by specifying the first
    line of the multiline value on the same line as the option starting
    immediately after the space after the equals sign (once again any extra
    spaces will be treated as part of the value). All subsequent lines have to
    be indented 4 spaces. Any characters after those 4 spaces are treated as
    part of the line. In fact the first line doesn't have to contain any text
    if you are using a multiline value, in which case the value will start
    with a ``\n`` character. Here are two examples:

    ::

        option1 = This
            is
                a
            multiline string
        option2 = 
            and
            so is this

    Note: The implementation doesn't enforce all the option naming conventions
    yet
    """
    if not os.path.exists(filename):
        raise Exception('No such file %r'%filename)
    if os.path.isdir(filename):
        raise Exception('%r is a directory, not a file'%filename)
    data = None
    try:
        # Open in binary mode to avoid Python doing clever things with line
        # endings
        fp = open(filename, 'rb')
        data = fp.read().decode('utf-8')
        fp.close()
        fp = None
    finally:
        if 'fp' in locals() and fp:
            fp.close()
        if data is None:
            raise Exception(
                'Could not read the data from %r, do you have the correct '
                'permissions and is it encoded as UTF8?'%filename
            )
    conf = {}
    cur_option = None
    cur_value = None
    for i, line in enumerate(data.split('\n')):
         if line.startswith('#'):
             # It is a comment
             continue
         elif line.startswith('    '):
             if i == 0:
                 raise SyntaxError('Line %s cannot start with four '
                     'spaces', i+1)
             # It is either a mistake, blank line or part of a multiline
             # value
             elif option is None:
                 raise SyntaxError('Indented line found but no option '
                     'specified')
             else:
                 # It is part of a multiline string
                 cur_value.append(line[4:])
         elif not line.strip():
             # Assume it is the end of a multiline string:
             if cur_option is not None:
                 conf[str(cur_option)] = '\n'.join(cur_value)
                 cur_option = None
                 cur_value = None
             continue
         elif (ord(line[0]) >= 65 and ord(line[0])<=90) or \
            (ord(line[0]) >= 97 and ord(line[0])<=122) or \
            ord(line[0]) == 95:
             # It is the start of an option
             parts = line.split(' = ')
             if len(parts) == 1:
                 error = "Expected the characters ' = ' on line %s"
                 if '=' in line:
                     error += ", not just an '=' on its own"
                 raise SyntaxError(error%(i+1))
             elif len(parts) > 2:
                 value = ' = '.join(parts[1:])
             else:
                 value = parts[1]
             # Extra whitespace after the option is ignored 
             option = parts[0].strip()
             if conf.has_key(option):
                 raise SyntaxError(
                     'The option %s found on line %s was already '
                     'specified earlier in the file'%(option, i+1)
                 )
             # Add the previous config option
             if cur_option is not None:
                 conf[str(cur_option)] = '\n'.join(cur_value)
             cur_option = option
             cur_value = [value]
         else:
             raise SyntaxError(
                 'Unexpected character at the start of line %s'%(i+1)
             ) 
    # Add the last config option
    if cur_option is not None:
        conf[cur_option] = '\n'.join(cur_value)
    #if not conf.has_key('app.filename'):
    #    conf['app.filename'] = filename
    return conf

class ConfigFileError(getopt.GetoptError):
    pass

def handle_option_error(conversion, base=None):
    if base:
        base = base+'.'
    else:
        base = ''
    errors = []
    for name, message in encode_error(conversion).items():
        errors.append(base+name+': '+message%dict(name=base[:-1]))
    error = conversion.error + '\n    ' + ('\n    '.join(errors))
    log.error(error)
    raise ConfigFileError(error)

def handle_section_error(bag, option, example):
    if bag and not bag.app.option:
        raise ConfigFileError(
            'No config options were found, have you specified a config '
            'file containing %r options, e.g. %s'%(
                option, 
                example,
            )
        )
    raise ConfigFileError(
        'Expected the config file to contain %r options, e.g. %s'%(
            option, 
            example,
        )
    )

def split_options(options):
    return Conversion(options).perform(
        decodeNestedRecord(depth=1)
    ).result

def parse_and_split_options_change_dir(service, filename):
    """\
    This function is where you can set up your settings. Ordinarily, 
    settings which you want end users to configure should go in the 
    config file, settings which the developer needs control over can
    go here.
    """
    if not os.path.exists(filename):
        raise getopt.GetoptError('No such file %r'%filename)
    os.chdir(os.path.join(*os.path.split(os.path.abspath(filename))[:-1]))
    options = parse_config(filename)
    # Split up the setting into parts
    option_group = split_options(options)
    return option_group


class PipeConfigError(Exception):
    pass

def dump_pipes(pipes):
    output = ''
    for pipe in pipes:
        output += pipe.name + " " + pipe.path
        for name, alias in pipe.aliases:
            output += ' '+name+'='+alias
        output += '\n'
    return output

def parse_pipes(path):
    if not os.path.exists(path):
        raise PipeConfigError("No such file %r"%path)
    fp = open(path, 'r')
    data = fp.read()
    fp.close()
    counter = 0
    pipes = []
    for line in data.split('\n'):
        counter += 1
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        while '  ' in line:
            line = line.replace('  ', ' ')
        parts = line.split(' ')
        aliases = []
        if len(parts) < 2:
            raise PipeConfigError("Syntax error on line %r, expected a module path"%counter)
        if len(parts) > 2:
            name, path, aliases_ = parts[0], parts[1], ' '.join(parts[2:])
            for alias in aliases_.split(','):
                alias = alias.strip()
                if not alias.count('=') == 1:
                    raise PipeConfigError("Alias %r on line %r should contain exactly one `=' sign"%(alias, counter))
                else:
                    aliases.append(AttributeDict(src=alias.split('=')[0].strip(), dst=alias.split('=')[1].strip()))
        else:
            name, path = parts
            aliases = []
        name = name.strip()
        path = path.strip()
        pipes.append(AttributeDict(name=name, path=path, aliases=aliases))
    return pipes

