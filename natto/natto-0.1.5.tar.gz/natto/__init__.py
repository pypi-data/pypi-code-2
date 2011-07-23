from cgi import escape
import re
import traceback
from time import time
import collections
import inspect as _inspect

from _css import css

__all__= ['natto', 'css']

#TODO#
# inject css into dom
# problems with recursions in modules (eg. re)

scalar_types = (basestring, int, float, bool)

container_tpl = u'<table class="natto_container"><tr><th title="traceback: %(title)s"><span class="label">%(label)s</span> &lt;%(th)s&gt;<span style="float:right"></span></th></tr><tr><td>%(content)s</td></tr></table>'
iterable_tpl  = u'<table class="natto gray-%(depth)s" style="width:100px;">%(rows)s</table>'
key_title_tpl = u'(%(name)s) %(path)s'
row_tpl       = u'<tr><th class="key %(key_class)s" id="natto_%(id)s" title="%(key_title)s">%(key)s</th><td><a name="natto_anchor_%(anchor_id)s" id="natto_anchor_%(anchor_id)s"></a>%(value_html)s</td></tr>'
value_tpl     = u'<div class="value type_%(value_type)s">%(value)s</div>'
docstring_tpl = u'<div class="docstring_container"><div class="docstring_expander" onclick="docstring_expander_click(this);"><div style="display:block;white-space:nowrap;">%(expander_text)s</div></div><div class="docstring">%(docstring)s</div></div>'
recursion_tpl = u'<div class="recursion" onmouseover="recursion_onmouseover(this, \'natto_%(id)s\')" onmouseout="recursion_onmouseout();">RECURSION AT ID %(id)s</div>'

javascript    = r'''
<script type="text/javascript">
function docstring_expander_click(elm) {
    if(elm.firstChild.style.display == 'none') {
        elm.firstChild.style.display = 'block';
        elm.style.backgroundImage=('url(data:image/gif;base64,R0lGODlhDgAOAKUfADg4OEZGRldXV2dnZ3V1dX9/f5ycnJ+fn6Ojo6ysrLGxsba2tru7u8DAwMXFxcfHx8rKytPT09fX193d3d7e3uDg4OXl5ejo6Onp6evr6+7u7vHx8fT09Pf39/z8/P7+/v////7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/iwAAAAADgAOAAAGaUDQZEgsDkEYkHLJVGIkn6h0GpVEPNisFhuBdL7fQgH8hTg4aDSBkEY7Gpv4YE6PbxoMjV7A7+s1DAsZg4MBAYSDCwoXjIwAAI2MCgkWlZaXlQkIFZydnpwIDwcUpKWmBw8gBqusrasgQQA7)');
        elm.nextSibling.style.display = 'none';
    } else {
        elm.firstChild.style.display = 'none';
        elm.style.backgroundImage=('url(data:image/gif;base64,R0lGODlhDgAOAIQbAFdXV39/f5ycnJ+fn6Ojo6enp7Gxsba2tru7u8DAwMXFxcfHx8rKytPT09fX193d3d7e3uDg4OPj4+jo6Onp6evr6+7u7vHx8fT09Pf39/z8/P7+/v////7+/v7+/v7+/iwAAAAADgAOAAAFWyBXPWRpVhvFrWy7Us4mz7TsNFqu73nDZMCgEMhQYI7I5FGRuDgD0KjzkkBYroCs9mpBHCrgsBh8MEzO6PTZUJC433B3gRCp2+91wmIA6fv/AwsbCgKFhocKGyEAOw==)');
        elm.nextSibling.style.display = 'table';
    }
}
function recursion_onmouseover(elm, natto_id) {
    node=elm.parentNode.parentNode;
    do{ node = node.parentNode; } while ( node.firstChild.id.lastIndexOf(natto_id+'_', 0) !== 0 );
    natto_th_node=node.firstChild;
    natto_old_recursion_key_style=natto_th_node.className;
    natto_th_node.className='key highlight';
}
function recursion_onmouseout(elm) {
    natto_th_node.className=natto_old_recursion_key_style;
}
function flash_anchor_jump(anchor_id){
    var anchor_elm = document.getElementById(anchor_id);
    var old_elm_style = anchor_elm.parentNode.childNodes[1].style.border;
    anchor_elm.parentNode.childNodes[1].style.border = '5px solid #ff96ce';
    setTimeout(function(){
        anchor_elm.parentNode.childNodes[1].style.border = old_elm_style;
    }, 1000)
}
function copy_original(target_elm, anchor_id){
    target_elm.innerHTML = document.getElementById(anchor_id).parentNode.innerHTML;
}
</script>
'''



def _reset__time():
    '''Sets the reference for the first natto _timestamp.'''
    globals()['last__time'] = time()

def _other(obj, options):

    if options['sort_attr']:
        sequence = sorted(dir(obj))
    else:
        sequence = dir(obj)

    for attr in dir(obj):

        if attr == '__abstractmethods__':
            continue

        if attr == '__dict__':
            attr_value = '...'
        else:
            attr_value = getattr(obj, attr)

        # __magics__ members
        if attr.startswith('__') and attr.endswith('__'):
            
            if options['magics']:
                if isinstance(attr_value, scalar_types):
                    yield (attr, attr_value)
                else:
                    yield (attr, str(attr_value))
            else:
                if options['doc'] and attr == '__doc__' and attr_value:
                    yield (attr, attr_value)

        elif attr.startswith('__') and options['privates'] == False:
            pass
        elif attr.startswith('_') and options['internals'] == False:
            pass
        else:
            yield (attr, attr_value)


def _natto(data, state, options):
    '''
    The recursive function that does all the work
    '''
    
    if options['max_i'] and state['id_i'] > options['max_i']:
        return None
    
    state['id_i'] += 1

    # scalars

    type_name = type(data).__name__
    key_css_class = 'other'

    if False \
        or _inspect.isbuiltin(data) \
        or (options['classes'] == False and _inspect.isclass(data)) \
        or _inspect.iscode(data) \
        or _inspect.isdatadescriptor(data) \
        or _inspect.isframe(data) \
        or _inspect.isfunction(data) \
        or _inspect.isgeneratorfunction(data) \
        or _inspect.isgetsetdescriptor(data) \
        or _inspect.ismemberdescriptor(data) \
        or _inspect.ismethod(data) \
        or _inspect.ismethoddescriptor(data) \
        or (options['modules'] == False and _inspect.ismodule(data)) \
        or _inspect.isroutine(data) \
        or _inspect.istraceback(data) \
        or type(data).__name__ == 'method-wrapper':
        
        
        if options['func_doc']:

            try:
                doc_str = '<div class="funcalike">%(funcalike)s</div><br />%(docstring)s' % {'funcalike':escape( str(data)), 'docstring':escape(data.__doc__,True)}
                doc_str = docstring_tpl % {'expander_text':escape(str(data), True), 'docstring':doc_str}
                
            except AttributeError:
                return value_tpl % {'value_type':'func' ,'value':escape(str(data), True)}
    
            return doc_str

        else:
            return value_tpl % {'value_type':'func' ,'value':escape(str(data), True)}

    if data is None:
        return value_tpl % {'value_type':'none' ,'value':data}

    if len(state['path']) > 0 and state['path'][-1] == '__doc__':
        #TODO# docutils rst parser?
        return docstring_tpl % {'expander_text':'expand', 'docstring':escape(data,True)}
    

    if isinstance(data, basestring):

        if isinstance(data, unicode):
            value_class = 'unicode'
        else:
            value_class = 'string'

        if data == '':
            value = '<div class="empty">&lt;empty string&gt;</div>'

        else:

            if options['max_str_len'] and len(data) > options['max_str_len']-3:
                value = data[:options['max_str_len']]+'...'

            value = str(data)

            if options['html_highlight']:

                value = re.sub(
                    "((?i)&lt;\/?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\"&gt;\s]+))?)+\s*|\s*)\/?&gt;)",
                    lambda m: r'<span class="html_tag">%s</span>' % m.group(0),
                    escape(value))

            else:
                value = escape(value, True)

            # highlight spaces at the line start/end and tabs everywhere in the string
            if options['show_whitespace']:
                value = re.sub(
                    r'(^ +)|( +$)',
                    lambda m: '<span class="border_spaces"> </span>' * (len(m.group(0)) ),
                    value,
                    0,
                    re.M)

                value = re.sub(
                    r'\t+',
                    lambda m: '<span class="tabs">\t</span>' * (len(m.group(0)) ),
                    value,
                    0)

        return value_tpl % {'value_type':value_class ,'value':value}


    if isinstance(data, bool):
        if data is True:
            value = 'True'
            value_class = 'bool_true'
        else:
            value = 'False'
            value_class = 'bool_false'

        return value_tpl % {'value_type':value_class ,'value':value}


    if isinstance(data, (int, float)):
        return value_tpl % {'value_type':'number' ,'value':data}

    # iterables

    rows = [] # holds our table rows
    
    if isinstance(data, dict):
        key_css_class = 'dict'
        sequence = ((key, value) for key, value in data.iteritems())

    elif _inspect.isgenerator(data):
        key_css_class = 'generator'
        sequence = ((key, value) for key, value in enumerate(data))

    elif isinstance(data, ( list, tuple, set, frozenset, collections.deque)):
        key_css_class = 'sequence'
        sequence = ((key, value) for key, value in enumerate(data))

    # everything else must be an object
    else:
        sequence = _other(data, options)
        
        rows.append( '<tr class="other_title"><th colspan="2">%(module)s - %(typename)s</th></tr>' % {
            'module':  type(data).__module__,
            'typename':type(data).__name__
        })
        
    try:
        length = len(data)
    except (AttributeError, TypeError): # generators etc.
        length = None

    if length == 0:
        return '<div class="empty">&lt;empty %s&gt;</div>' % type_name

    obj_id = id(data)

    # In order to understand recursion...
    if obj_id in state['visited']:
        return recursion_tpl % {'id':obj_id}

    # when no_rep is on, sequences and dicts are only printed when they first appear
    if options['no_rep'] and obj_id in state['ids']:
        jump_link = '<a href="#natto_anchor_%s" onclick="flash_anchor_jump(\'natto_anchor_%s\')">jump to</a>' % (obj_id, obj_id)
        copy_link = '<a href="" onclick="javascript:copy_original(this.parentNode.parentNode, \'natto_anchor_%s\'); return false;">copy here</a>' % (obj_id)
        return '<div class="repetition">REPETITION: %s/%s</div>' % (jump_link, copy_link)

    if options['no_rep']:
        state['ids'].add(obj_id)

    state['visited'].append(obj_id)

    for key, value in sequence:
        if key == '_inspect': continue
        
        state['path'].append(key)

        path = '.'.join( [str(item) for item in state['path']] )

        if options['max_v'] and len(rows) >= options['max_v']:

            if length:
                skipped = length - options['max_v']
            else:
                skipped = '?'

            rows.append(row_tpl % {
                'id'         : 'dummy_%s' % state['id_i'],
                'key_class'  : 'type_%s' % key_css_class,
                'key_title'  : '(%s) %s' % (type(data).__name__, path),
                'key'        : '...',
                'anchor_id'  : str(id(value)),
                'value_html' : '<div class="skipped">[%s skipped] (max_v=%s)</div>' % (skipped, options['max_v'])
            })
            state['path'].pop()
            break
        
        # if something goes wrong in the next call to _natto, print the error
        # instead of the value and stop here
        try:
            # backup the state so it can be restored if the next iteration fails
            state_bak = state['path'][:]
            
            if options['max_h'] and len(state['path']) > options['max_h']:
                value_html = '<div class="max_depth">max_h reached (%s)</div>' \
                             % options['max_h']
            else:
                value_html = _natto(value, state, options) # next iteration
                
                if not value_html: # max_i
                    rows.append(row_tpl % {
                        'id'         : 'dummy_%s' % state['id_i'],
                        'key_class'  : 'type_%s' % key_css_class,
                        'key_title'  : '(%s) %s' % (type(data).__name__, path),
                        'key'        : '...',
                        'anchor_id'  : str(id(value)),
                        'value_html' : '<div class="max_i">max_i reached (%s)</div>' \
                                       % options['max_i']
                    })
                    state['path'].pop()
                    break
                
        except Exception as strerror:
            state['path'] = state_bak # rollback the state
            value_html = 'UNEXPECTED natto ERROR: %s' % strerror
        
        rows.append(row_tpl % {
            'id'         : '%s_%s' % (id(value), state['id_i'] ),
            'key_class'  : 'type_%s' % key_css_class,
            'key_title'  : key_title_tpl % {'name':type(data).__name__, 'path':path },
            'key'        : escape(str(key)),
            'anchor_id'  : str(id(value)),
            'value_html' : value_html
        })

        state['path'].pop()
    
    
    rows[-1] = re.sub(r'<th class="key ', '<th class="key last_item ', rows[-1], 1)

    state['visited'].pop()
    
    return iterable_tpl % {'depth':len(state['path']) ,'rows':''.join(rows)}

def natto(
        data, 
        classes = True,
        doc = True,
        func_doc = True,
        html_highlight = True,
        internals = False,
        label = '',
        modules = True,
        magics = False,
        privates = False,
        max_h = None,
        max_i = None,
        max_v = None,
        max_str_len = 1000,
        no_rep = True,
        show_whitespace = True,
        sort_attr = False,
        strip_address = True,
        with_css = False,
        ):
    """return a HTML representation of data
    
    :param data: the subject you want to inspect
    :param doc: docstrings for objects are usually displayed even if magics is
    disabled. This can be changed by setting doc to `False`
    :param classes: ...
    :param func_doc: show expandable docstrings for functions
    :param html_highlight: highlight html tags in strings
    :param internals: show _hidden attributes
    :param label: text for a label
    :param modules: ...
    :param magics: show __special__ attributes
    :param privates: show __private attributes
    :param max_h: maximum horizontal depth
    :param max_i: maximum total items
    :param max_v: maximum vertical items per structure
    :param max_str_len: maximum length for strings...
    :param no_rep: don't repeat objects, show the jump_to/copy_here links
    :param show_whitespace: color the whitespace in strings
    :param sort_attr: ...
    :param strip_address: discard the memory address for object.__str__
    :param with_css: prepend the output with a stylesheet tag containing the css
    if set to false, you have to take care of the css yourself (natto.css)
    
    :return: :class:`unicode`
    """
    options = _inspect.getargvalues(_inspect.currentframe()).locals
    
    state = {'path':[],'visited':[], 'id_i':0, 'ids':set()}

    html = container_tpl % {
        'title'   : escape(str(traceback.extract_stack()[-2]), True),
        'th'      : '{0}:{1}'.format(traceback.extract_stack()[-2][0], traceback.extract_stack()[-2][1]),
        'label'   : options['label'],
        'content' : _natto(data=data, state=state, options=options),
    }
    if options['strip_address']:
        html = javascript + re.sub(r' at 0x\S+&gt;', '&gt;', html, 0, re.M)
        
    if options['with_css']:
        html = '<style type="text/css">%s</style>%s' %  (css, html)

    return html

