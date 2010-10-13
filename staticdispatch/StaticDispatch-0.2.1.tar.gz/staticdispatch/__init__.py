import os
import logging
import mimetypes

from bn import AttributeDict, uniform_path
from httpkit.helper.response import forbidden, not_found
from pipestack.ensure import ensure_function_bag as ensure

log = logging.getLogger(__name__)

def resolveResource():
    def resolveResource_constructor(bag, name, *k, **p):
        url_cache = {}

        from conversionkit import Conversion, chainConverters
        from recordconvert import toRecord
        from configconvert import existingDirectory, handle_option_error, handle_section_error
        
        def unicodeSplit(separator=','):
            def unicodeSplit_converter(conversion, state):
                if not isinstance(conversion.value, (unicode)):
                    raise Exception('Expected the input to be Unicode string')
                conversion.result = [x.strip() for x in conversion.value.split(separator)]
            return unicodeSplit_converter

        if not bag.app.option.has_key(name):
            handle_section_error(bag, name, "'%s.site_root'"%(name,))

        static_converter = chainConverters(
            toRecord(
                missing_errors =  [
                    "The required option '%s.%%(key)s' is missing"%name, 
                    (
                        'site_root',
                    )
                ],
                empty_errors = [
                    "The option '%s.%%(key)s' cannot be empty"%name, 
                    (
                        'site_root',
                    )
                ],
                missing_defaults = {
                    'ignore_extensions': u'py, flo',
                },
                converters=dict(
                    site_root = existingDirectory(uniform_path=True),
                ),
                allow_extra_fields=False,
                msg_field_not_allowed=\
                   "The config file does not support the '%s.%%s' option."%name,
                msg_fields_not_allowed=\
                   "The '%s.*' options in the config file are invalid. The "
                   "options '%%s' and '%%s' are not supported."%name,
            ),
        )
        conversion = Conversion(bag.app.option[name]).perform(static_converter)
        if not conversion.successful:
            handle_option_error(conversion, name)
        else:
            bag.app.config[name] = conversion.result

        def enter(bag):
            bag[name] = AttributeDict()
            # Make sure the root path ends with a /
            path_info = bag.environ.get('PATH_INFO', '/')
            if not path_info.startswith('/'):
                log.warning('PATH_INFO %r doesn\'t start with a \'/\' character')
                path_info = '/'+path_info
            resource = uniform_path(os.path.join(bag.app.config[name].site_root, path_info[1:]))
            path = u''
            script = u''
            if not resource.startswith(bag.app.config[name].site_root):
                # Trying to get a file it shouldn't have access to
                log.error('File %r not under site root %r', resource, bag.app.config[name].site_root)
                return
            # Rather than just returning a 404 we'll see if anywhere along
            # the path there is an index.app file. We'll then set the
            # script and path based on the position of the first index.app
            # along that path, caching the lookup as we go
            path_to_check = path_info[1:]
            fallback_counter = 1000
            counter = 2
            while counter and fallback_counter:
                fallback_counter -= 1
                counter -= 1
                if fallback_counter == 0:
                    raise Exception('Reached maximum recursion limit for directory checks')
                log.debug('Checking %r in %r', path_to_check, os.path.join(bag.app.config[name].site_root))
                directory = os.path.join(bag.app.config[name].site_root, path_to_check)
                if os.path.exists(directory) and os.path.isdir(directory) and os.path.exists(os.path.join(directory, 'index.app')):
                    # We've found our app
                    script = path_to_check
                    path = path_info[len(script):]
                    log.info('Adding path %r and script %r to resolve cache. Using %r as the resource', path, script, resource)
                    url_cache[resource] = path, script
                    bag[name]['app'] = uniform_path(os.path.join(bag.app.config[name].site_root, script))
                    break
                elif counter == 0:
                    log.debug('No index.app file for %r', resource)
                    if not os.path.exists(resource):
                        return 
                    # Otherwise the code below will set the resource
                    log.debug('Setting resource as %r', resource)
                    bag[name]['resource'] = resource
                    return 
                else:
                    res = path_to_check.rfind('/')
                    if res > 0:
                        path_to_check = path_to_check[:res]
                        # reset the counter
                        counter = 2
                    else:
                        path_to_check = ''
            else:
                path, script = url_cache[resource]
            # Set the variables
            log.debug('Setting resource as %r', resource)
            bag[name]['resource'] = resource
            # XXX These should be used in app dispatch
            bag[name]['path'] = path
            bag[name]['script'] = script
        return AttributeDict(enter=enter)
    return resolveResource_constructor

def staticDispatch(
    ignore_extensions = [],
):
    def staticDispatch_constructor(bag, name, aliases=None, *k, **p):
        if aliases is None:
            aliases = {'resolve': 'resolve'}

        from conversionkit import Conversion, chainConverters
        from recordconvert import toRecord
        from stringconvert import unicodeToBoolean, unicodeToUnicode
        from configconvert import handle_option_error
        
        def unicodeSplit(separator=','):
            def unicodeSplit_converter(conversion, state):
                if not isinstance(conversion.value, (unicode)):
                    raise Exception('Expected the input to be Unicode string')
                conversion.result = [x.strip() for x in conversion.value.split(separator)]
            return unicodeSplit_converter

        def checkContentType():
            def checkContentType_converter(conversion, state):
                if not isinstance(conversion.value, (unicode)):
                    raise Exception('Expected the input to be Unicode string, not %r'%conversion.value)
                if not len(conversion.value.split('/')) == 2:
                    raise Exception(
                        "Invalid default content type. Expected the format "
                        "'text/html'"
                    )
                conversion.result = unicode(conversion.value)
            return checkContentType_converter

        static_converter = chainConverters(
            toRecord(
                missing_defaults = {
                    'default_content_type': u'application/octet-stream',
                    'ignore_extensions': u'py, flo',
                    'directory_index': '',
                },
                converters=dict(
                    default_content_type = checkContentType(),
                    ignore_extensions = unicodeSplit(),
                    directory_index = unicodeToUnicode(),
                ),
                allow_extra_fields=False,
                msg_field_not_allowed=\
                   "The config file does not support the '%s.%%s' option."%name,
                msg_fields_not_allowed=\
                   "The '%s.*' options in the config file are invalid. The "
                   "options '%%s' and '%%s' are not supported."%name,
            ),
        )
        conversion = Conversion(bag.app.option.get(name, {})).perform(static_converter)
        if not conversion.successful:
            handle_option_error(conversion, name)
        else:
            bag.app.config[name] = conversion.result

        @ensure(aliases['resolve'])
        def enter(bag):
            bag[name] = AttributeDict()
            if not bag[aliases['resolve']].has_key('resource'):
                log.debug('No resource was resolved so can\'t serve a static file')
                # No resource could be resolved
                return
            resource = bag[aliases['resolve']]['resource']
            # Check if this resolves to the directory index (it doesn't if we have an index.app in there)
            if os.path.isdir(resource) and bag.app.config[name].directory_index:
                resource = os.path.join(resource, bag.app.config[name].directory_index)
            # Deal with CGI scripts
            extension = resource.split('.')[-1]
            if extension not in bag.app.config[name].ignore_extensions:
                # Deal with static files
                type, encoding = mimetypes.guess_type(resource)
                if not type:
                    type = str(bag.app.config[name].default_content_type)
                try:
                    fp = open(resource, 'rb')
                except (IOError, OSError), e:
                    log.warning('Could not read %r. Error was: %s', resource, e)
                    return forbidden(bag)
                else:
                    def result_iterator():
                        try:
                            for line in fp:
                                if line:
                                    yield line
                        finally:
                            fp.close()
                    bag.http_response.status = '200 OK'
                    bag.http_response.header_list = [dict(name='Content-Type', value=type)]
                    bag.http_response.body_format = 'bytes'
                    if bag.environ.get('QUERY_STRING'):
                        import datetime
                        days = 1
                        expires = expires_from_datetime(datetime.datetime.now()+datetime.timedelta(days))
                        bag.http_response.header_list.append(dict(name='Cache-Control', value='max-age=%s'%(3600*24*days)))
                        bag.http_response.header_list.append(dict(name='Expires', value=expires))
                    bag.http_response.body = result_iterator()
                    bag.interrupt_flow(application_handled = True)
            else:
                log.debug('Extension is one that should not be served')
        return AttributeDict(enter=enter)
    return staticDispatch_constructor

import time

weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [
    None,
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]

def expires_from_datetime(when):
    year, month, day, hh, mm, ss, wd, y, z = when.timetuple()
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd],
        day, 
        monthname[month], 
        year,
        hh, 
        mm, 
        ss,
    )

# New naming
ResolvePipe = resolveResource()
StaticPipe = staticDispatch()

