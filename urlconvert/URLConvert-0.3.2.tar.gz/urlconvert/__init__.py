# -*- coding: utf-8 -*-

import logging
import re
from urllib import quote, unquote, quote_plus, unquote_plus

from conversionkit.exception import ConversionKitError
from conversionkit import Conversion, set_error, set_result, \
   chainConverters, chainPostConverters, tryEach, toDictionary, \
   noConversion
from bn import AttributeDict


#
# Set up logging
#

log = logging.getLogger('urlconvert')
log.debug("The module 'urlconvert' is being imported")

#
# Exceptions
#

class URLConvertError(ConversionKitError):
    pass

class RuleParseError(Exception): 
    pass

#
# Main interface
#

class RuleSet(object):
    def __init__(self, rules=None, cache_generation=True, cache_matching=True):
        if rules is not None and not rules:
            raise Exception('No rules specified')
        self.to_vars_converter = convertAndCache(
            [r.to_vars for r in rules],
            cache=cache_matching,
            convert_type='match', 
        )
        self.to_url_converter = convertAndCache(
            [r.to_url for r in rules],
            cache=cache_generation,
            convert_type='generate', 
        )

    def match_url(self, url, script=None):
        url_parts = Conversion(url).perform(_to_parts).result
        if script is not None:
            if script.endswith('/'):
                raise URLConvertError(
                    "According to the WSGI spec SCRIPT_NAME cannot end with "
                    "a '/' character, so neither should the 'script' argument"
                )
            url_parts['script'] = script
            url_parts['path'] = url_parts['path'][len(script)+1:]
        result = self.match(url_parts)
        return result
    
    def match(self, url_parts):
        log.debug('Converting URL parts %r to routing variables', url_parts)
        return Conversion(url_parts).perform(self.to_vars_converter)
    
    def generate_url(self, routing_vars, default_url_parts):
        d = default_url_parts.copy()
        rv = dict([(unicode(k),unicode(v)) for k,v in routing_vars.items()])
        conversion = self.generate(rv, default_url_parts)
        if conversion.successful:
            res = conversion.result
            d.update(res.url_parts)
            # @@@ Should really use a post converter
            result = Conversion(AttributeDict(url=build_url(**d), extra=res.extra)).perform(noConversion())
            return result
        raise Exception('No matching generation rule could be found')

    def generate(self, routing_vars, default_url_parts=None):
        log.debug('Converting routing variables %r to URL parts', routing_vars)
        if default_url_parts is None:
            value = dict(vars=routing_vars, current=dict())
        else:
            value = dict(vars=routing_vars, current=default_url_parts)
        return Conversion(value).perform(self.to_url_converter)

#
# Cache
#

def convertAndCache(converters, cache=True, convert_type=None):
    if cache:
        cached = {}
    def convertAndCache_converter(conversion, service=None):
        parts = conversion.value
        if cache:
            if convert_type == 'generate':
                a = parts['vars'].items()
                b = parts['current'].items()
                a.sort()
                b.sort()
                p = (tuple(a), tuple(b),)
            elif convert_type == 'match':
                p = parts.items()
                p.sort()
                p = (tuple(p), None)
            else:
                raise URLConvertError('Unknown convert_type for caching %r'%convert_type)
            if p in cached:
                log.debug(
                    'Converting from cache: %r, convert_type: %r, result: %r',
                    parts, 
                    convert_type,
                    cached[p],
                )
                conversion.result = cached[p]
                return

        log.debug('Not cached: %r, convert_type: %r', parts, convert_type)
        log.debug('%s converters available', len(converters))
        log.debug('Trying each rule in turn...')
        conversion.perform(
            tryEach(
                converters, 
                stop_on_first_result=True, 
                MSG_NONE_SUCCESSFUL='No rule matched',
            )
        )
        if conversion.successful:
            set_result(conversion, AttributeDict(conversion.result))
            if cache:
                cached[p] = conversion.result
                log.info(
                    'Converting and adding to cache: %r, convert_type: %r, result: %r',
                    parts, 
                    convert_type,
                    cached[p],
                )
            else:
                log.debug(
                    'Converting, not caching: %r, convert_type: %r, result: %r',
                    parts, 
                    convert_type,
                    conversion.result,
                )
        else:
            log.info('%r. (%r)', conversion.error, parts)
    return convertAndCache_converter

#
# Split Rules and URLs
#

def urlToParts():
    """\
    Takes a URL or rule and splits it up into a scheme, host, port and path.
    """
    def urlToParts_converter(conversion, service=None):
        url = conversion.value
        if not isinstance(url, unicode):
            raise URLConvertError(
                'Expected a URL specified as a Unicode string'
            )
        log.debug('Splitting the URL %r', url)
        # Remove the query string component, we don't want to dispatch on that.
        parts = url.split(u'?')
        if len(parts) > 2:
            conversion.error = (
                "The URL can contain no more than one '?' character"
            )
            return
        elif len(parts) == 2:
            url, query = parts
        else:
            query = None
        # Now work on the rest of it
        parts = url.split(u'://')
        if len(parts) > 2:
            conversion.error = "The string '://' should only occur once"
            return
        elif len(parts) == 1:
            conversion.error = (
                "Please specify the scheme part of the URL too, eg "
                "'https://...'"
            )
            return
        scheme, rest = parts
        rest = rest.split(u'/')
        if u':' not in rest[0]:
            host = rest[0]
            port = None
            # No port was explicitly specified so make a best guess:
            environ = service and hasattr(service, 'environ') and service.environ or None
            if environ:
                port = unicode(
                    environ.get(
                        'X_PORT_FORWARDED_FOR', 
                        environ.get('SERVER_PORT'),
                    )
                )
            if not port:
                if scheme == 'https':
                    port = u'443'
                else:
                    port = u'80'
        else:
            host, port = rest[0].split(u':')
        path = u'/'.join(rest[1:])
        conversion.result = dict(
            scheme = scheme,
            host = host,
            port = port,
            path = path,
        )
        if query is not None:
            conversion.result['query'] = query
    return urlToParts_converter

# Use the one instance internally
_to_parts = urlToParts()

def ruleToParts():
    def ruleToParts_converter(conversion, service=None):
        child_conversion = Conversion(conversion.value).perform(_to_parts)
        if not child_conversion.successful:
            conversion.error = child_conversion.error
            return
        parts = child_conversion.result
        path_parts = parts['path'].split(u'|')
        if len(path_parts) > 2:
            raise URLConvertError("A rule can only contain one '|' character")
        elif len(path_parts) == 2:
            parts['path'] = path_parts[1]
            parts['script'] = path_parts[0]
        else:
            parts['script'] = u'{*}'
        if not parts.has_key('query'):
            parts['query'] = u'{*}'
        conversion.result = parts
    return ruleToParts_converter
_rule_to_parts = ruleToParts()

#
# Generation Converters
#
import copy
def removeExtras(add):
    """\
    Remove the extra variables to the dictionary (as long as they don't conflict)
    """
    def removeExtras_converter(conversion, service=None):
        current = conversion.value['current']
        vars = conversion.value['vars']
        for k, v in add.items():
            k = unicode(k)
            if not unicode(conversion.value['vars'].get(k)) == unicode(v):
                conversion.error = (
                    "This rule doesn't match, the vars don't contain the %r "
                    "variable which is present in the add dictionary for the "
                    "rule" % k
                )
                return 
        result = dict(current=current, vars={}) 
        for k, v in vars.items():
            k = unicode(k)
            if k not in add:
                result['vars'][unicode(k)] = v
        conversion.result = result
    return removeExtras_converter

def joinVars(add):
    def joinVars_post_converter(conversion, service=None):
        # There shouldn't have been problems with the conversions
        if not conversion.successful:
            return 
        # First check they all received the same input variables 
        # and while we're at it, make a list of all the matched variables
        children = conversion.children.values()
        if not children:
            raise NotImplementedError('Not sure what to do in this case, will wait until this is raised')
            set_result(conversion, result)
        input = children[0].result[0]
        matched = children[0].result[2]
        counter = 0
        for child in children[1:]:
            counter += 1
            for var in child.result[2]:
                if var not in matched:
                    matched.append(var)
            if child.result[0] != input:
                raise URLConvertError(
                    "Item %s of the generators didn't receive the same input "
                    "variables as item 0" % counter
                )
        # Now we can start the real processing.
        # 1. Find out if all the variables which were matched
        variables = input['vars'].keys()
        #for k, v in add.items():
        #    if k in input['vars'].keys() and 
        #    variables.pop(variables.index(k))
        variables.sort()
        matched.sort()
        if variables != matched:
            log.debug(
                ('Not all the input variables were matched against this rule. '
                'Input != Matched: %r != %r'), 
                variables,
                matched,
            )
            set_error(
                conversion,
                'Not all the input variables were matched against this rule'
            )
            return
        # 2. If they do, assemble the parts
        result = dict([(k, v[1]) for k, v in conversion.result.items()])
        set_result(conversion, result)
    return joinVars_post_converter

def generateDynamicHost(host_part):
    variables = []
    def generateDynamicHost_converter(conversion, service=None):
        if not conversion.value.has_key('vars') or \
           not conversion.value.has_key('current'):
            raise URLConvertError(
                "The conversion should be a dictionary with 'vars' and "
                "'current' keys, not %r" % conversion.value
            )
        vars = conversion.value['vars']
        current = conversion.value['current']
        log.debug(
            'Trying to match the host vars %r against the rule %r', 
            vars, 
            host_part,
        )
        # Parse the variables now if they haven't already been parsed
        if not variables:
            variables.append(parse_vars(host_part))
        matched = {}
        for k in variables[0]:
            if k in vars:
                matched[k] = vars[k]
            else:
                conversion.error = (
                    'The variable %r in the rule could not be found in the '
                    'variables supplied'%k
                )
                return
        # Create the URL:
        url = host_part[:]
        # Note, not all the fvars have to exist in the Rule
        for k, v in matched.items():
            if not isinstance(v, unicode):
                raise URLConvertError(
                    'Expected the variable %r to correspond to a unicode '
                    'string, not %r' % (k, v)
                )
            url = url.replace('{'+k+'}', v)
        log.debug('Success, returning URL %r', url)
        conversion.result = (conversion.value, url, matched.keys())
    return generateDynamicHost_converter

def generateStaticOrDynamic(part, expected_value=None, dynamic=None):
    if expected_value is dynamic is None:
        raise URLConvertError("You must specify 'expected_value' or 'dynamic'")
    def generateStaticOrDynamic_converter(conversion, service=None):
        current = conversion.value['current']
        vars = conversion.value['vars']
        if dynamic and not current.has_key(part):
            raise URLConvertError('No default URL data present for %r'%part)
        if dynamic is None:
            conversion.result = (conversion.value, expected_value, [])
            #conversion.error = (
            #    "Static part %s expected value %r doesn't match current "
            #    "URL value %r" % (part, expected_value, current[part])
            #)
        else:
            if dynamic not in vars:
                conversion.error = (
                    'The %s variable %s required for this rule to match '
                    'is not one of the variables'%(part, dynamic)
                )
            else:
                conversion.result = (
                    conversion.value, 
                    current[part],
                    [dynamic],
                )
    return generateStaticOrDynamic_converter

def generateDynamicPath(part, path_part):
    variables = []
    def generateDynamicPath_converter(conversion, service=None):
        if not conversion.value.has_key('vars') or \
           not conversion.value.has_key('current'):
            raise URLConvertError(
                "The conversion should be a dictionary with 'vars' and "
                "'current' keys, not %r" % conversion.value
            )
        #if not conversion.value['vars']:
        #    raise Exception('The vars have been removed! %r'%conversion.value)
        vars = conversion.value['vars']
        current = conversion.value['current']
        log.debug(
            'Trying to match the path vars %r against the rule %r', 
            vars, 
            path_part,
        )
        # Parse the variables now if they haven't already been parsed
        if not variables:
            variables.append(parse_vars(path_part))
        # Coulf do the encoding here
        matched = {}
        for k in variables[0]:
            if k in vars:
                matched[k] = vars[k]
            else:
                conversion.error = (
                    'The variable %r in the rule could not be found in the '
                    'variables supplied'%k
                )
                return
        # Create the URL:
        url = path_part[:]
        # Note, not all the fvars have to exist in the Rule
        for k, v in matched.items():
            if not isinstance(v, unicode):
                raise URLConvertError(
                    'Expected the variable %r to correspond to a unicode '
                    'string, not %r' % (k, v)
                )
            url = url.replace('{'+k+'}', v)
        log.debug('Success, returning URL %r', url)
        conversion.result = (conversion.value, url, matched.keys())
    return generateDynamicPath_converter

def generateStaticOrDynamic(part, expected_value=None, dynamic=None):
    if expected_value is dynamic is None:
        raise URLConvertError("You must specify 'expected_value' or 'dynamic'")
    def generateStaticOrDynamic_converter(conversion, service=None):
        current = conversion.value['current']
        vars = conversion.value['vars']
        if dynamic and not current.has_key(part):
            raise URLConvertError('No default URL data present for %r'%part)
        if dynamic is None:
            conversion.result = (conversion.value, expected_value, [])
            #conversion.error = (
            #    "Static part %s expected value %r doesn't match current "
            #    "URL value %r" % (part, expected_value, current[part])
            #)
        else:
            if dynamic not in vars:
                conversion.error = (
                    'The %s variable %s required for this rule to match '
                    'is not one of the variables'%(part, dynamic)
                )
            else:
                conversion.result = (
                    conversion.value, 
                    current[part],
                    [dynamic],
                )
    return generateStaticOrDynamic_converter

#
# Matching Converters
#

def missingKey(parts, input):
    def missingKey_converter(conversion, service=None):
        if input == 'match':
            value = conversion.value
        elif input == 'generate':
            value = conversion.value['current']
        else:
            raise URLConvertError("Invalid 'input' argument %r"%input)
        for key in parts:
            if not key in value:
                raise URLConvertError(
                    'Cannot compare rule because no %r key was specified ' 
                    'in the URL parts'%key
                )
        conversion.result = conversion.value
    return missingKey_converter

def mergeParts():
    """\
    Takes a dictionary of dictionaries and merges them into a single
    dictionary, immediately returning an error conversion if the same 
    variable is used in different dictionaries and has a different 
    value in each.
    """
    def mergeParts_post_converter(conversion, service=None):
        if conversion.successful:
            result = {}
            for part, item in conversion.result.items():
                # Any correctly converted parts exist only as a dictionary
                if isinstance(item, dict):
                    for name, value in item.items():
                       if result.has_key(name):
                           if result[name] != value:
                               set_error(
                                   conversion,
                                   'No match: different values %s and %s '
                                   'present for the variable %s' % (
                                       result[name], 
                                       value, 
                                       name
                                   )
                               ) 
                               return
                       else:
                           result[name] = value
            set_result(conversion, result)
    return mergeParts_post_converter

_no_conversion = noConversion()
def addExtras(add):
    """\
    Add the extra variables to the dictionary (as long as they don't conflict)
    """
    def addExtras_post_converter(conversion, service=None):
        if conversion.successful:
            for k, v in add.items():
                if conversion.value.has_key(k):
                    raise URLConvertError(
                        "The 'add' dictionary cannot contain the same key %r "
                        "as a routing variable defined in the rule"%k
                    )
                conversion.result[k] = v
                conversion.children[k] = Conversion(v).perform(_no_conversion)
    return addExtras_post_converter

def matchStatic(part, expected_value):
    if not isinstance(expected_value, unicode):
        raise URLConvertError(
            "Expected the 'expected_value' argument to be a Unicode string"
        )

    def matchStatic_converter(conversion, service):
        value = conversion.value
        if not isinstance(value, unicode):
            raise URLConvertError(
                'Expected the %s to be a Unicode string'%part
            )
        if value == expected_value:
            # This part doesn't appear in the routing variables
            conversion.result = {}
        else:
            conversion.error = (
                'The %s %r does not match %r expected by '
                'the rule'%(part, value, expected_value)
            )
    return matchStatic_converter

def matchDynamic(part, dynamic):
    """\
    Match the part to the routing variable given by ``dynamic``.
    """
    def matchDynamic_converter(conversion, service):
        value = conversion.value
        if not isinstance(value, unicode):
            raise URLConvertError(
                'Expected the %s to be a Unicode string'%part
            )
        conversion.result = {dynamic: value}
    return matchDynamic_converter

def matchDynamicDomain(host_part):
    """\
    Match the host part of a URL against the variables defined in the
    string ``host_part``.
    """
    regex = []

    def matchDynamicDomain_converter(conversion, service):
        host = conversion.value
        if not isinstance(host, unicode):
            raise URLConvertError(
                'Expected the host to be a Unicode string'
            )
        # Compile the regular expression if it hasn't be compiled
        if not regex:
            regex.append(parse_re(host_part, part='host'))
        match = regex[0].search(host)
        if match:
            vars = {}
            vars.update(match.groupdict())
            log.debug('Success, returning vars %r', vars)
            conversion.result = vars
        else:
            conversion.error = 'Domain not matched'
            log.debug('Failed: %r', conversion.error)
    return matchDynamicDomain_converter

def matchDynamicPath(part, path_part):
    """\
    Match the path or script part of a URL against the variables defined in 
    the string ``path_part``.
    """
    regex = []
    def matchDynamicPath_converter(conversion, service):
        value = conversion.value
        if not isinstance(value, unicode):
            raise URLConvertError(
                'Expected the %s to be a Unicode string, not %r'%(part, value)
            )
        # Compile the regular expression if it hasn't be compiled
        if not regex:
            # We have to use a list so Python doesn't get confused about
            # scope
            regex.append(parse_re(path_part, part=part))
        match = regex[0].search(value)
        if match:
            vars = {}
            vars.update(match.groupdict())
            log.debug('Success, returning vars %r', vars)
            conversion.result = vars
        else:
            conversion.error = '%s %r not matched against %r'%(
                part.capitalize(),
                value, 
                path_part
            )
            log.debug('Failed: %r', conversion.error)
    return matchDynamicPath_converter

#
# Creating converters from a rule
#

def rule(rule, add=None, extra=None):
    if not isinstance(rule, unicode):
        raise URLConvertError(
            'Expected the rule to be specified as a Unicode string'
        )
    if add is not None:
        for k in parse_vars(rule):
            # This gets checked later too, but better to do it now.
            if k in add:
                raise URLConvertError(
                    "The 'add' dictionary cannot contain the same key %r "
                    "as a routing variable defined in the rule"%k
                )
        for k, v in add.items():
            if not isinstance(k, unicode):
                raise URLConvertError(
                    'Expected the key %r to be a Unicode string'%k
                )
            if not isinstance(v, unicode):
                raise URLConvertError(
                    'Expected the value %r to be a Unicode string'%v
                )
        add = add.copy()

    # Start making the chain
    chain = []

    # Split up the rule
    parts = Conversion(rule).perform(_rule_to_parts).result

    # Now create a match and generate converter for each part.
    match = {}
    generate = {}

    # Start with the easy ones which either don't exist, take a static part, 
    # or have a single dynamic part
    for key in ['scheme', 'query', 'port']:
        if parts[key] not in [u'{}', u'{*}']:
            if parts[key].startswith('{'):
                if not parts[key].endswith('}'):
                    raise URLConvertError(
                        "Expected the %s part to end with '}' since it "
                        "can only contain one routing variable" % key
                    )
                var = parts[key][1:-1]
                if '{' in var or '}' in var:
                    raise URLConvertError(
                        'The %s part of the rule is invalid'%key
                    )
                match[key] = matchDynamic(part=key, dynamic=var)
                generate[key] = generateStaticOrDynamic(part=key, dynamic=var)
            elif '{' in parts[key] or '}' in parts[key]:
                raise URLConvertError(
                    'The %s part of the rule is invalid'%key
                )
            else:
                match[key] = matchStatic(key, parts[key])
                generate[key] = generateStaticOrDynamic(
                    part=key, 
                    expected_value=parts[key],
                )
    if parts['host'] != u'{*}':
        if u'{*}' in parts['host']:
            raise URLConvertError(
                "The host part %r is invalid, you cannot use {*} as well "
                "as text or named variables."%parts['host']
            )
        if not re.match(
            '[A-Za-z0-9](([A-Za-z0-9\-])+.)*',
            parts['host'][:].replace('{','a').replace('}','a'),
        ):
            raise URLConvertError('The host name is invalid')
        if not '{' in parts['host']:
            # Static text. Check the characters.
            match['host'] = matchStatic('host', parts['host'])
            generate['host'] = generateStaticOrDynamic(
                part='host', 
                expected_value=parts['host'],
            )
        else:
            match['host'] = matchDynamicDomain(parts['host'])
            generate['host'] = generateDynamicHost(parts['host'])
    # The path and script
    for key in ['path', 'script']:
        if parts[key] not in [u'{*}']:
            #if u'{}' in parts[key]:
            #    raise URLConvertError(
            #        "The %s part %r is invalid, you cannot use {} as well as "
            #        "named variables, only instead of them"%(key, parts[key])
            #    )
            if not re.match(
                '([A-Za-z0-9\-\%\/\:\"@&=+\$\,_\.\!\~\*\'\(\)])*',
                parts[key][:].replace('{','a').replace('}','a')
            ):
                raise URLConvertError('The %s contains invalid characters'%key)
            if not '{' in parts['path']:
                # Static text. Check the characters.
                match[key] = matchStatic(key, parts[key])
                generate[key] = generateStaticOrDynamic(
                    part=key, 
                    expected_value=parts[key],
                )
            else:
                match[key] = matchDynamicPath(key, parts[key])
                generate[key] = generateDynamicPath(key, parts[key])

    # Finally, create a converter capable of parsing all this data
    post_converters = [
        toDictionary(match), 
        mergeParts(),
    ]
    if add is not None:
        post_converters.append(addExtras(add))
    post_converters.append(extraVariables(extra))
    to_vars = chainConverters(
        missingKey(match.keys(), 'match'),
        chainPostConverters(*post_converters)
    )
    to_url = chainPostConverters(
       chainConverters(
            removeExtras(add or {}),
            # This is expecting a dictionary, we have a tuple, and want each 
            # of the generate converters called for each tuple.
            # ie: We need a for_each with a key for each.
            tryEach(
                generate.values(),
                stop_on_first_result=False, 
                stop_on_first_error=True, 
                children_keys=generate.keys()
            ),
        ),
        joinVars(add or {}),
        extraVariables(extra, 'url_parts'),
    )
    return AttributeDict(dict(to_vars=to_vars, to_url=to_url))

def extraVariables(extra, key='vars'):
    def extraVariables_post_converter(conversion, state):
        if conversion.successful:
            vars = conversion.result
            set_result(conversion, AttributeDict(extra=extra, **{key:vars}))
    return extraVariables_post_converter

#
# Rule handling helpers
#

def parse_re(rule, part):
    """\
    Parse the Unicode string ``rule`` to a regular expression. ``part`` can
    be ``host`` or ``path`` and determines which characters need escaping.

    Some examples:

    ::

        hello.{name}.com`` becomes ``^\.hello\.(?P<name>[a-zA-Z-%_\.0-9]+)\.com$
        /hello/{name}`` becomes ``^\/hello\/(?P<name>[a-zA-Z-%_\.0-9]+)$

    """
    if part == 'host':
        r = rule[:].replace('.','\.')
        r = r.replace('{}','([a-zA-Z-%_0-9]+)')
    elif part in ['path', 'script']:
        r = rule[:].replace('/','\/')
        r = r.replace('{}','([a-zA-Z-%_0-9]+)')
    else:
        raise URLConvertError('Unknown URL part %r'%part)
    r = r.replace('{','(?P<').replace('}','>[a-zA-Z-%_\.0-9]+)')
    r = '^'+r+'$'
    regex = re.compile(r)
    log.debug(
        '%s part %r formatted to %r and compiled to %r', 
        part.capitalize(), 
        rule, 
        r,
        regex,
    )
    return regex

def parse_vars(rule):
    vars = []
    i = 0
    current_var = ''
    mode = 'url' 
    while i < len(rule):
        if mode == 'url':
            if rule[i] == '{':
                mode = 'var'
            elif rule[i] == '}':
                raise RuleParseError(
                    "Found '}' without an opening '{' before it"
                )
        else:
            if rule[i] == '{':
                raise RuleParseError(
                    "Found '}' without an opening '{' before it"
                )
            elif rule[i] == '}':
                mode = 'url'
                if current_var not in vars:
                    vars.append(current_var)        
                current_var = ''
            else:
                current_var+=rule[i]
        i += 1
    vars.sort()
    log.debug('Rule %r parsed to vars %r', rule, vars) 
    return vars

#
# Encoders
#

def plainEncode(encoding):
    def plainEncode_converter(conversion, state=None):
        try:
            conversion.result = conversion.value.encode(encoding)
        except Exception, e:
            conversion.error = str(e)
    return plainEncode_converter

def plainDecode(encoding):
    def plainDecode_converter(conversion, state=None):
        try:
            conversion.result = conversion.value.decode(encoding)
        except Exception, e:
            conversion.error = str(e)
    return plainDecode_converter

scheme_regex = re.compile('[a-zA-Z]([a-zA-Z0-9\+\.\-]*)')

def matchScheme(make_lowercase=True, allowed_values=None):
    """\
    A converter which takes a fully decoded scheme as a Unicode string and
    ensures it is valid.

    The RFC states that scheme names::
    
         consist of a sequence of characters beginning with a
         lower case letter and followed by any combination of lower case
         letters, digits, plus ("+"), period ("."), or hyphen ("-").  For
         resiliency, programs interpreting URI should treat upper case letters
         as equivalent to lower case in scheme names (e.g., allow "HTTP" as
         well as "http").
     
            scheme        = alpha *( alpha | digit | "+" | "-" | "." )

    In practice for web applications the scheme will only be ``http`` or
    ``https`` so you can specify ``allowed_values`` if you prefer to be more
    restrictive. 

    Since schemes are case insensitive it is often easier to just work with
    lowercase schemes. Unless you set ``make_lowercase()`` to ``False``, 
    schemes returned from this converter will be made lowercase.
    """
    if allowed_values is not None and make_lowercase:
        allowed_values = [value.lower() for value in allowed_values]
    def matchScheme_converter(conversion, state=None):
        scheme = conversion.value
        if not isinstance(scheme, unicode):
            raise URLConvertError(
                'Expected the scheme to be a unicode string'
            )
        if allowed_values is not None:
            if (make_lowercase() and scheme.lower() not in allowed_values) \
               or (scheme not in allowed_values):
                conversion.error = (
                    'The scheme %r is not one of the allowed values %r'%(
                        scheme, 
                        allowed_values
                    )
                )
                return
        else:
            match = scheme_regex.match(scheme)
            if not match:
                conversion.error = 'The scheme %r is not valid'%(scheme)
                return
        if make_lowercase:
            conversion.result = scheme.lower()
        else:
            conversion.result = scheme
    return matchScheme_converter

domain_label_regex = re.compile('([0-9]+) || [a-zA-Z0-9]([a-zA-Z0-9\-]*)[a-zA-Z0-9]')

def matchHost():
    """\
    The RFC describes ther host as::

        This is a sequence of domain labels separated by
        ".", each domain label starting and ending with an alphanumeric
        character and possibly also containing "-" characters.

    We follow this here.
    """

    def matchHost_converter(conversion, state=None):
        host = conversion.value
        if not isinstance(host, unicode):
            raise URLConvertError(
                'Expected the host to be a unicode string'
            )
        if not len(host) >= 2:
            conversion.error = 'Hosts should be at least two characters long'
            return
        labels = host.split('.')
        for label in labels:
            match = domain_label_regex.match(label)
            if not match:
                conversion.error = 'The %s part of the host is not valid'
                return
        conversion.result = host
    return matchHost_converter

def matchPort():
    """\
    Matches that the port represents an integer in the range 1-65535. 
    """
    def matchPort_converter(conversion, state):
        port = conversion.value
        if not isinstance(port, unicode):
            raise URLConvertError(
                'Expected the port to be a unicode string'
            )
        try:
            p = int(port)
        except (ValueError, TypeError), e:
            conversion.error = '%s is not a valid port'
            return 
        else:
            if p < 1 or p > 65535:
                conversion.error = '%s is not a valid port'
            else:
                conversion.result = port
    return matchPort_converter

path_regex = re.compile("[0-9a-zA-Z\-_\.\!~\*'\(\)\:\@\&\=\+\$\,\/]*")

def matchPath():
    """
    This converter takes a permissive approach and doesn't encode any characters
    which according to the RFC don't need to be encoded::
        
        alphanumeric: 0123456789
                      ABCDEFGHIJKLMNOPQRSTUVWXYZ
                      abcdefghijklmnopqrstuvwxyz
        
        mark:         -_.!~*'()
        
        unreserved:   alphanumeric
                      mark
        
        phar:         unreserved
                      escaped
                      :@&=+$,
    
    The only tricky bit is how to handle semi-colons because in theory path
    segments can be split into parameters separated by a ';' but unlike this
    situation with a ``/`` the URLConvert doesn't split on that
    character. This converter assumes that the ``;`` should *not* be escaped so

    This means the path_info segments may include the following characters with
    no escaping::
    
        0123456789
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        abcdefghijklmnopqrstuvwxyz
        -_.!~*'()
        :@&=+$,
        ;

    Any other characters in a variable value to be used as a segment get
    encoded to the double hex octet form. For example ``/`` becomes ``%2F``. 
    """
    def matchPath_converter(conversion, state=None):
        path = conversion.value
        if not isinstance(path, unicode):
            raise URLConvertError(
                'Expected the path to be a unicode string'
            )
        match = path_regex.match(path)
        if not match:
            conversion.error = 'The %s part of the host is not valid'
        else:
            conversion.result = path
    return matchPath_converter

def makeUnicode():
    def makeUnicode_converter(conversion, state=None):
        conversion.result = unicode(conversion.value)
    return makeUnicode_converter

def decodeScript(encoding=None):
    """\
    Decodes all ``%`` escapes from a URL script part to Unicode.
    
    ``encoding`` specifies the encoding from which the value should be decoded.
    If set to None, no decoding is performed.
    """
    return decodePart('script', unquote, encoding)

def decodeQuery(encoding=None):
    """\
    Decodes all ``%`` escapes from a URL script part to Unicode.
    
    ``encoding`` specifies the encoding from which the value should be decoded.
    If set to None, no decoding is performed.
    """
    return decodePart('script', unquote_plus, encoding)

def decodePath(encoding=None):
    """\
    Decodes all ``%`` escapes from a URL path segment to Unicode.
    
    ``encoding`` specifies the encoding from which the value should be decoded.
    If set to None, no decoding is performed.
    """
    return decodePart('path', unquote, encoding)

def decodePart(part, unquote=unquote, encoding=None):
    def decodePart_converter(conversion, state=None):
        value = conversion.value
        if not isinstance(value, unicode):
            raise URLConvertError(
                'Expected the %s to be a unicode string'%part
            )
        if isinstance(value, unicode):
            value = str(value)
        if encoding is not None:
            conversion.result = unquote(value).decode(encoding)
        else:
            conversion.result = unicode(unquote(value))
    return decodePart_converter

def encodePart(part, encoding=None, quote=quote):
    def encodePart_converter(conversion, state=None):
        value = conversion.value
        if not isinstance(value, unicode):
            raise URLConvertError(
                'Expected the %s to be a unicode string'%part
            )
        # One of the rare occurences we encode first because we want the  
        # binary encoding quoted.
        if encoding is not None:
            value = value.encode(encoding)
        conversion.result = quote(value).decode('ascii')
    return encodePart_converter

def encodePath(encoding=None, quote=quote):
    """\
    RFC 3986 states that the percent-encoded byte
    values should be decoded as UTF-8.
    
    http://tools.ietf.org/html/rfc3986 section 2.5.
    """
    return encodePart('path', encoding, quote)

def encodeScript(encoding=None):
    """\
    """
    return encodePart('script', encoding, quote)

def encodeQuery(encoding=None):
    """\
    """
    return encodePart('query', encoding, quote_plus)

def matchScript():
    """\
    Same as ``matchPath()``
    """
    def matchScript_converter(conversion, state=None):
        script = conversion.value
        if not isinstance(script, unicode):
            raise URLConvertError(
                'Expected the script to be a unicode string'
            )
        match =  path_regex.match(script)
        if not match:
            conversion.error = 'The %s part of the script is not valid'
        else:
            conversion.result = script
    return matchScript_converter

def matchQuery():
    """
    I couldn't find the documentation for query strings so I'm assuming it is
    the same as the the path component for the timebeing
    """
    def matchQuery_converter(conversion, state=None):
        query = conversion.value
        if not isinstance(query, unicode):
            raise URLConvertError(
                'Expected the query to be a unicode string'
            )
        match =  path_regex.match(query)
        if not match:
            conversion.error = 'The %s part of the query is not valid'
        else:
            conversion.result = query
    return matchQuery_converter

#
# Helper functions for building the initial URL
#

decode_scheme = chainConverters(makeUnicode(), matchScheme(), plainDecode('utf8'))
decode_host = chainConverters(makeUnicode(), matchHost(), plainDecode('utf8'))
decode_port = chainConverters(makeUnicode(), matchPort(), plainDecode('utf8'))
decode_script = chainConverters(makeUnicode(), matchScript(), decodeScript('utf8'))
decode_path = chainConverters(makeUnicode(), matchPath(), decodePath('utf8'))
decode_query = chainConverters(makeUnicode(), matchQuery(), decodeQuery('utf8'))

def extract_scheme(service, converter=None):
    """\
    Calculate the scheme from a services dictionary.
    
    Attempts to get the scheme by trying each of these in order:

    * The ``.config.server.display_scheme`` attribute of the ``service`` object if 
      such an attribute exists
    * The ``wsgi.url_scheme`` key in the environ
    * Based on the port (with a call to ``extract_port()``)

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the scheme once it has been converted. If ``None``, 
    the ``decode_scheme`` converter is used.
    """
    if converter is None:
        converter = decode_scheme
    scheme = None
    if hasattr(service, 'config') and hasattr(service.config, 'server') and \
       hasattr(service.config.server, 'display_scheme'):
        scheme = service.config.app.display_scheme
    else:
        environ = service and hasattr(service, 'environ') and service.environ or None
        if environ:
            scheme = environ.get('wsgi.url_scheme')
            if not scheme:
                port = extract_port(service)
                if port:
                    if port == '80':
                        scheme = 'http'
                    elif port == '443':
                        scheme = 'https'
    if not scheme:
        raise Exception('No scheme could be calculated from the service')
    return Conversion(scheme).perform(converter).result

def extract_host(service, converter=None):
    """\
    Calculate the host from a services dictionary.

    Attempts to get the host by trying each of these in order:

    * The ``.config.server.display_host`` attribute of the ``service`` object if 
      such an attribute exists
    * The first part of an the ``X_FORWARDED_FOR`` key in the environ (can't be trusted)
    * The ``HTTP_HOST`` key in the environ (can't be trusted)
    * The ``SERVER_NAME`` key in the environ (can be trusted, but might not be the
      host the user should use)

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the host once it has been converted. If ``None``, 
    the ``decode_host`` converter is used.
    """
    if converter is None:
        converter = decode_host
    host = None
    if hasattr(service, 'config') and hasattr(service.config, 'server') and \
       hasattr(service.config.server, 'display_host'):
        host = service.config.server.display_host
    else:
        environ = service and hasattr(service, 'environ') and service.environ or None
        if environ:
            if environ.has_key('X_FORWARDED_FOR'):
                host = environ['X_FORWARDED_FOR'].split(',')[0].strip()
            if not host: 
                host = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        if not host:
            raise Exception('No host could be calculated from the service')
        else:
            host = host.split(':')[0]
    return Conversion(host).perform(converter).result

def extract_port(service, converter=None):
    """\
    Calculate the port from a services dictionary. Returns the port as a
    unicode string.

    Attempts to get the host by trying each of these in order:

    * The ``.config.server.display_port`` attribute of the ``service`` object if 
      such an attribute exists
    * The ``X_PORT_FORWARDED_FOR`` key in the environ (totally unofficial)
    * The ``SERVER_PORT`` key in the environ (can be trusted, but might not be the port
      the user should use)

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the port once it has been converted. If ``None``, 
    the ``decode_port`` converter is used.
    """
    if converter is None:
        converter = decode_port
    environ = service and hasattr(service, 'environ') and service.environ or None
    if environ:
        port = str(environ.get('X_PORT_FORWARDED_FOR', environ.get('SERVER_PORT')))
    if not port:
        raise Exception('No port could be calculated from the service')
    return Conversion(port).perform(converter).result

def build_url(scheme, host, port=None, script=None, path=None, query=None, try_to_hide_port=True):
    output = ['%s://%s' % (scheme, host)]
    if port:
        if not try_to_hide_port or (scheme == 'https' and port!='443') or (scheme == 'http' and port!='80'):
            output.append(':%s'%port)
    if script:
        output.append('/')
        output.append(script)
    if path:
        output.append('/')
        output.append(path)
    if query:
        output.append('?%s'%query)
    return ''.join(output)

def extract_path(service, converter=None):
    """
    Calculate the path from a services dictionary. The returned path does not
    include the first ``/``.
    
    Attempts to get the path by trying each of these in order:

    * The ``PATH_INFO`` variable in ``environ`` which is expected to start 
      with a ``/`` character.

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the path once it has been converted. If ``None``, 
    the ``decode_path`` converter is used.
    """
    if converter is None:
        converter = decode_path
    environ = service and hasattr(service, 'environ') and service.environ or None
    if environ:
        path = environ.get('PATH_INFO')
        if path is None:
            return None
        if not path.startswith('/'):
            raise URLConvertError("Expected the PATH_INFO %r to start with '/'"%(path))
        path = path[1:]
    return Conversion(path).perform(converter).result

def extract_script(service, converter=None):
    """
    Calculate the script name from a services dictionary.
    
    Attempts to get the script by trying each of these in order:

    * The ``SCRIPT_NAME`` variable in ``environ``

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the script once it has been converted. If ``None``, 
    the ``decode_query`` converter is used.
    """
    if converter is None:
        converter = decode_script
    environ = service and hasattr(service, 'environ') and \
       service.environ or None
    if environ:
        script = environ.get('SCRIPT_NAME')
        if script is None:
            return None
        if script.startswith('/'):
            script = script[1:]
        if script.endswith('/'):
            raise URLConvertError(
                "The SCRIPT_NAME %r cannot end with a '/' character" %(
                    script 
                )
            )
            #script = script[:-1]
    return Conversion(script).perform(converter).result

def extract_query(service, converter=None):
    """
    Calculate the query string from a services dictionary.
    
    Attempts to get the query by trying each of these in order:

    * The ``QUERY_STRING`` variable in ``environ``

    The ``converter`` argument is an optional converter which is used to 
    decode and validate the query once it has been converted. If ``None``, 
    the ``decode_query`` converter is used.
    """
    if converter is None:
        converter = decode_query
    environ = service and hasattr(service, 'environ') and \
       service.environ or None
    if environ:
        query = environ.get('QUERY_STRING')
    if query is None:
        return None
    return Conversion(query).perform(converter).result

def extract_url_parts(
    service, 
    with_port=True, 
    with_script=True, 
    with_query=True,  
    scheme_converter=None, 
    host_converter=None, 
    port_converter=None, 
    path_converter=None, 
    script_converter=None, 
    query_converter=None,
):
    parts = dict(
        scheme = extract_scheme(service, scheme_converter),
        host = extract_host(service, host_converter),
        path = extract_path(service, path_converter),
    )
    if with_port:
        parts['port'] = extract_port(service, port_converter)
    if with_script:
        parts['script'] = extract_script(service, script_converter)
    if with_query:
        parts['query'] = extract_query(service, query_converter)
    for k, v in parts.items():
        if v is None:
            del parts[k] 
    return parts

def extract_url(
    service, 
    with_port=False, 
    with_script=False, 
    with_query=False,  
    scheme_converter=None, 
    host_converter=None, 
    port_converter=None, 
    path_converter=None, 
    script_converter=None, 
    query_converter=None,
):
    parts = extract_url_parts(
        service,
        with_port,
        with_script,
        with_query,
        scheme_converter,
        host_converter,
        port_converter,
        path_converter,
        script_converter,
        query_converter,
    )
    return build_url(**parts)
