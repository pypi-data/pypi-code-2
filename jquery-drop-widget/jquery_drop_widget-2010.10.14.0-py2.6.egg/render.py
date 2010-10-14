"""
Render our jQuery Drop Widgets
"""

import time
import re
import os

# Pygments: Code highlighting: http://pygments.org/
#NOTE(g): jquery_drop_widget's Python Egg imports this module
import pygments
import pygments.lexers, pygments.formatters


# These JS and CSS files are added to EVERY Output object before any custom
#   js_include/css_include, which are appended after these defaults
#TODO(g): Do this better.  Im forcing them to use my chosen libraries, at this
#   revision...
#JS_INCLUDE_DEFAULT = ["js/jquery-1.4.2.min.js",
#                      "js/jquery-ui-1.8.2.custom.min.js"]
#CSS_INCLUDE_DEFAULT = ["css/redmond/jquery-ui-1.8.2.custom.css"]
#TODO(g): Shoudlnt this just happen in the page headers?  Those are defaults,
#   anything specified should be additional...
JS_INCLUDE_DEFAULT = []
CSS_INCLUDE_DEFAULT = []


def MakeIdSafe(text, safe_char='-'):
  """Make text safe to be inserted into an HTML tag ID field."""
  unsafe_chars = '\',."<>!@#$%^&*(){}[]=+_`~;: \n'
  
  # Cycle through the unsafe characters, and replace any found with safe ones
  for char in unsafe_chars:
    if char in text:
      text = text.replace(char, safe_char)
  
  return text


class Output:
  
  def __init__(self, js_include=None, css_include=None):
    # The body contains the body of the widget element.  This is what will be
    #   inserted into an HTML page via some kind of templating or something.
    #   That problem is left to the developer, but dropSTAR has a method for this
    #   to be done easily, if you're using dropSTAR.
    self.body = ''
    
    # "js" is a list of javascript files to import into this page.  This allows
    #   dynamic importing of JS files, so widgets can specify their requirements
    #   and append new ones as found.  Templates into "%(js_include)s"
    #NOTE(g): It is up to the developer to ensure none of their JS files conflict.
    self.js_include = []
    for include in JS_INCLUDE_DEFAULT:
      if include not in self.js_include:
        self.js_include.append(include)
    if js_include:
      for include in js_include:
        if include not in self.js_include:
          self.js_include.append(include)
    
    # "css" is like "js" in that it compiles a list of required CSS files, so
    #   they can be dynamically added to the page.  Templates into "%(css_include)s"
    self.css_include = []
    for include in CSS_INCLUDE_DEFAULT:
      if include not in self.css_include:
        self.css_include.append(include)
    if css_include:
      for include in css_include:
        if include not in self.css_include:
          self.css_include.append(include)
    
    # Any scripts we want added to the page can be put in here, and will be
    #   mixed in with all the other script.  Putting them in order is respected
    #   on rendering.
    self.js = []
    
    # Any cookies found will be written.  If they are simple keypair, they they
    #   are recorded as session cookies.  
    self.cookies = {}
  
  
  def __repr__(self):
    output = self.body
    
    # Append Javascript to the end of the body
    #TODO(g): Do this better...  Some of this needs to wait until after the
    #   page has loaded, so really we need to use this twice, perhaps...
    if self.js:
      output += '\n<script>\n'
      
      for js in self.js:
        output += js + '\n'
      
      output += '\n</script>\n'
    
    return output
  
  
  def __iadd__(self, text):
    """In place add, to our self.body."""
    self.body += str(text)
    
    return self


def Value(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  output += '<div id="%s">%s</div>\n' % (id, content)
  
  return output


def Button_Link(id, content, options=None, data=None, cookies=None, headers=None):
  """Button: Made out of an A HREF tag."""
  output = Output()
  
  output += '''<span id="%s"><a href="#" id="%s-link" class="ui-state-default ui-corner-all" style="padding: .4em 1em .4em 20px;text-decoration: none;position: relative;"><span class="ui-icon ui-icon-newwin" style="margin: 0 5px 0 0;position: absolute;left: .2em;top: 50%%;margin-top: -8px;"></span>%s</a></span>''' % (id, id, content)
  
  if options and 'click' in options:
    func = options['click']
  else:
    func = ''
  
  click = '''$('#%s-link').unbind('click');$('#%s-link').click(function(){%s});''' % (id, id, func)
  output.js.append(click)
  
  return output


def Button(id, content, options=None, data=None, cookies=None, headers=None):
  """Button: Made out of a BUTTON tag."""
  output = Output()
  
  #output += '''<span id="%s"><a href="#" id="%s-link" class="ui-state-default ui-corner-all" style="padding: .4em 1em .4em 20px;text-decoration: none;position: relative;"><span class="ui-icon ui-icon-newwin" style="margin: 0 5px 0 0;position: absolute;left: .2em;top: 50%%;margin-top: -8px;"></span>%s</a></span>''' % (id, id, content)
  
  output += '''<button id="%s" class="fg-button ui-state-default ui-corner-all" type="button">%s</button>''' % (id, content)
  
  if options and 'click' in options:
    func = options['click']
  else:
    func = ''
  
  #click = '''$('#%s-link').unbind('click');$('#%s-link').click(function(){%s});''' % (id, id, func)
  button = '''
    //all hover and click logic for buttons
    $("#%s")
    .hover(
      function(){ 
        $(this).addClass("ui-state-hover"); 
      },
      function(){ 
        $(this).removeClass("ui-state-hover"); 
      }
    )
    .click(function(){
      %s
    })
    .mousedown(function(){
        $(this).parents('.fg-buttonset-single:first').find(".fg-button.ui-state-active").removeClass("ui-state-active");
        if( $(this).is('.ui-state-active.fg-button-toggleable, .fg-buttonset-multi .ui-state-active') ){ $(this).removeClass("ui-state-active"); }
        else { $(this).addClass("ui-state-active"); }	
    })
    .mouseup(function(){
      if(! $(this).is('.fg-button-toggleable, .fg-buttonset-single .fg-button,  .fg-buttonset-multi .fg-button') ){
        $(this).removeClass("ui-state-active");
      }
    });
  ''' % (id, func)
  output.js.append(button)
  
  return output


def Input(id, content, options=None, data=None, cookies=None, headers=None):
  """Input to RPC"""
  output = Output()

  if options == None:
    options = {}

  output += '<span id="div_%s">\n' % id

  button_options = {'click':'''RPC('%s', {'text':$('#%s').val()}); $('#%s').val(''); return false;''' % (options['rpc'], id, id)}
  output = str(Button('input_button_%s' % id, options.get('title', 'Enter'), button_options))
  
  size = options.get('size', 20)
  
  output += '''<input type="text" id="%s" size="%s" maxlength="120" value="%s">''' % (id, size, content)

  output += '</span>\n'

  output += '''
  <script>
    // Enters submits comments on the wall
    $('#%s').keypress(function(event) {
      if (event.keyCode == '13') {
         //event.preventDefault();
         RPC('%s', {'text':$('#%s').val()});
         $('#%s').val('');
       }
    });
  </script>
  ''' % (id, options['rpc'], id, id)
  
  return output


def Tabs(id, content_dict, options=None, data=None, cookies=None, headers=None):
  """content is dict of strings, the strings match the tab names.
  
  Order is options['tabs'] list, which lists the tabs in order.  If not present
  tabs will be displayed in alphabetical order from content_dict.
  """
  output = Output()
  
  # Get the sorted order for our tabs
  if options and 'tabs' in options:
    order = options['tabs']
  else:
    order = content_dict.keys()
    order.sort()
  
  # Create the opening DIV
  output += '<div id="%s">\n' % id
  
  # Create the tab row
  output += '<ul>\n'
  
  # Create the tab row entries
  for count in range(0, len(order)):
    if options and 'labels' in options and options['labels'] and order[count] in options['labels']:
      output += '<li><a href="#%s-%d">%s</a></li>\n' % (id, count, options['labels'][order[count]])
    else:
      output += '<li><a href="#%s-%d">%s</a></li>\n' % (id, count, order[count])
  output += '</ul>\n'
  
  # Create the tab content
  for count in range(0, len(order)):
    output += '<div id="%s-%d">\n' % (id, count)
    output += str(content_dict[order[count]])
    output += '</div>\n' 

  # Create the closing DIV
  output += '</div>\n'

  selected_tab = 'tabs[%s]' % id
  print selected_tab
  if not options or 'selected' not in options or selected_tab not in options['selected']:
    selected = 0
  else:
    selected = int(options['selected'][selected_tab])
  
  # This JS is needed to product this tab
  output.js.append("$('#%s').tabs('destroy'); $('#%s').tabs({selected: $.cookie('tab_%s')||0});" % (id, id, id))
  
  # Specify all the tabs we need to collect to save cookies before reloading
  #   any data that may reload the tabs
  output.js.append('tabs["%s"] = true;' % id)
  
  
  return output


def Table(id, content_list, options=None, data=None, cookies=None, headers=None):
  """content is list of dicts."""
  output = Output()
  
  # Get the headers from the first element in the content_list
  if options and 'order' in options:
    headers = options['order']
  elif content_list:
    headers = content_list[0].keys()
    headers.sort()
  else:
    headers = []
  
  if options and 'width' in options:
    width = 'width:%s;' % options['width']
  else:
    width = ''
  
  # Table open and header
  output += '''
  <span id="%s"><table class="ui-widget ui-widget-content" style="%s">
    <thead>
      <tr class="ui-widget-header ">
  ''' % (id, width)
  
  # Table header rows
  for header in headers:
    if options and 'labels' in options and header in options['labels']:
      output += '<th>%s</th>\n' % options['labels'][header]
    else:
      output += '<th>%s</th>\n' % header
  
  # Table header close and body open
  output += '''
      </tr>
    </thead>
    <tbody id="processes_body">
  '''
  
  # Table body rows
  for item in content_list:
    output += '<tr>\n'
    for header in headers:
      output += '<td>%s</td>\n' % item[header]
    output += '</tr>\n'
  
  # Table close
  output += '''
    </tbody>
  </table></span>
  '''
  
  return output


def PowerTable(id, content_list, options=None, data=None, cookies=None, headers=None):
  """TODO(g): Retire this stupid name, and use the jQuery Plugin Author's name."""
  return DataTable(id, content_list, options=options, data=data, cookies=cookies, headers=headers)


def DataTable(id, content_list, options=None, data=None, cookies=None, headers=None):
  """content is a list of dicts.  Has sortable fields, filtering, pagination, scrolling.
  
  TODO(g): Credit all jQuery Plugin authors, in docstrings, and also in a
      credits list, with URLs to the sites so new versions can be attained.
  TODO(g): Come up with a packaging design to share these things so they are
      easy to segment and include (and try to get it accepted by jQuery people?)
  """
  output = Output()
  
  # Get the headers from the first element in the content_list
  if options and 'order' in options:
    headers = options['order']
  elif content_list:
    try:
      headers = content_list[0].keys()
      headers.sort()
    except KeyError, e:
      #TODO(g): This is a problem...  No log() here, because this is a stand
      #   alone library...
      headers = []
  else:
    headers = []
  
  # Get dynamic width
  if options and 'width' in options:
    width = 'width:%s;' % options['width']
  else:
    width = 'width:100%;'
  
  # Get dynamic height
  if options and 'height' in options:
    height = '"sScrollY": "%s"' % options['height']
  else:
    height = '"sScrollY": "200px"'
  
  # Create the ID for the data table.  Must be different, so we can still
  #   replace the content
  data_tables_id = '%s__dt' % id
  
  # Table open and header
  output += '''
  <div id="%s" style="%s"><table id="%s" class="ui-widget ui-widget-content" style="%s">
    <thead class="ui-widget-header">
      <tr>
  ''' % (id, width, data_tables_id, width)
  
  # Table header rows
  for header in headers:
    if options and 'labels' in options and header in options['labels']:
      output += '<th>%s</th>\n' % options['labels'][header]
    else:
      output += '<th>%s</th>\n' % header
  
  # Table header close and body open
  output += '''
      </tr>
    </thead>
    <tbody id="%s_body" class="ui-widget-content">
  ''' % id
  
  # Table body rows
  for item in content_list:
    output += '<tr>\n'
    for header in headers:
      if header in item:
        output += '<td class="%s">%s</td>\n' % (header, item[header])
      else:
        output += '<td>&nbsp;</td>\n'
      
    output += '</tr>\n'
  
  # Table close
  output += '''
    </tbody>
  </table></div>
  '''
  
  # Create data table options
  dt_options = ''
  if options and 'sort' in options:
    dt_options += ', "aaSorting": [%s] ' % str(options['sort'])
  
  # Create data table
  data_table_js = '''\
%s = $('#%s').dataTable( {
  "bPaginate": false,
  "bDestroy": true,
  //"bScrollCollapse": true,
  "bAutoWidth": false,
  "bJQueryUI": true,
  %s
  %s
});
''' % (data_tables_id, data_tables_id, height, dt_options)

  output.js.append(data_table_js)
  
  return output


def Image(id, content, options=None, data=None, cookies=None, headers=None):
  """Content is the IMG SRC value."""
  output = Output()
  
  # Create the image, and set the timestamp so it reloads properly each time
  #TODO(g): Specify reload times, if any.  Dont just hard code this...
  output += '<img id="%s" class="reload_90" src="%s?timestamp=%s">' % (id, content, int(time.time()))
  
  return output




def TypeFormat(text):
  text = str(text)
  if text.startswith('<type '):
    text = text[6:-1]
  
  text = text.replace('<', '&lt;').replace('>', '&gt;')
  
  if text.startswith("'") and text.endswith("'"):
    text = text[1:-1]
  
  return text


MAX_VALUE_STR_LENGHT = 80

def _GetTreeItems(data, id_prefix='', parent=None):
  """Returns a list of items (dicts), which have parents listed."""
  items = []
  
  if type(data) == dict:
    for key in data:
      item = {}
      item['key'] = key
      item['id'] = MakeIdSafe('%s_%s' % (id_prefix, key))
      item['kind'] = TypeFormat(type(data[key]))
      
      if type(data[key]) in (dict, list, tuple):
        item['icon'] = 'folder'
      else:
        item['icon'] = 'file'
      
      item['value'] = str(data[key])[:MAX_VALUE_STR_LENGHT]
      if parent:
        item['parent'] = parent
      items.append(item)
      
      # Recurse and add children
      if type(data[key]) in (dict, list, tuple):
        children = _GetTreeItems(data[key], item['id'], parent=item['id'])
        items += children
  
  # Sequences
  elif type(data) in (list, tuple):
    for count in range(0, len(data)):
      value = data[count]
      
      item = {}
      item['key'] = count
      item['id'] = MakeIdSafe('%s_%s' % (id_prefix, count))
      item['kind'] = TypeFormat(type(data[count]))
      
      if type(value) in (dict, list, tuple):
        item['icon'] = 'folder'
      else:
        item['icon'] = 'file'
      
      item['value'] = str(data[count])[:MAX_VALUE_STR_LENGHT]
      if parent:
        item['parent'] = parent
      items.append(item)
      
      # Recurse and add children
      if type(value) in (dict, list, tuple):
        children = _GetTreeItems(value, item['id'], parent=item['id'])
        items += children
  
  else:
    key = '_'
    item = {}
    item['key'] = key
    item['id'] = MakeIdSafe('%s_%s' % (id_prefix, key))
    item['kind'] = TypeFormat(type(data))
    item['value'] = str(data)[:MAX_VALUE_STR_LENGHT]
    if parent:
      item['parent'] = parent
    items.append(item)
  
  return items


def TableTree(id, content, options=None, data=None, cookies=None, headers=None):
  """content is dict OR list (containing dicts, to be useful)"""
  output = Output()
  
  # Get all the items in a flat list, with their parents marked, so they can
  #   be displayed in a non-flat hierarchy
  tree_items = _GetTreeItems(content)
  
  output += '''
<table id="%s" class="ui-widget ui-widget-content">
  <thead class="ui-widget-header">
    <tr>
      <th>Key</th>
      <th>Kind</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody class="ui-widget-content">
  ''' % id
  
  # Add all our tree items
  for item in tree_items:
    item_id = item['id']
    item_child = ''
    if 'parent' in item:
      item_child = 'class="child-of-%s"' % item['parent']
    icon = item.get('icon', 'file') # Default as file, not folder.  Improve this
    key = item['key']
    kind = item['kind']
    value = item['value']
    
    output += '''
    <tr id="%s" %s>
      <td class="initial"><span class="%s">%s</span></td>
      <td>%s</td>
      <td>%s</td>
    </tr>
    ''' % (item_id, item_child, icon, key, kind, value)

  
  output += '''\
  </tbody>
</table>
  '''
  
  output.js.append('$("#%s").treeTable();' % id)
  
  return output


def DictTableTree(id, content, options=None, data=None, cookies=None, headers=None):
  """Returns a Tree Table of a dictionary or list, showing the type and value
  for each.
  
  content is dict OR list (containing dicts, to be useful)
  """
  output = Output()
  
  # Get all the items in a flat list, with their parents marked, so they can
  #   be displayed in a non-flat hierarchy
  tree_items = _GetTreeItems(content)
  
  output += '''
<table id="%s" class="ui-widget ui-widget-content">
  <thead class="ui-widget-header">
    <tr>
      <th>Key</th>
      <th>Type</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody class="ui-widget-content">
  ''' % id
  
  # Add all our tree items
  for item in tree_items:
    item_id = item['id']
    item_child = ''
    if 'parent' in item:
      item_child = 'class="child-of-%s"' % item['parent']
    icon = item.get('icon', 'file') # Default as file, not folder.  Improve this
    key = item['key']
    kind = item['kind']
    value = item['value']
    
    output += '''
    <tr id="%s" %s>
      <td class="initial"><span class="%s">%s</span></td>
      <td>%s</td>
      <td>%s</td>
    </tr>
    ''' % (item_id, item_child, icon, key, kind, value)

  
  output += '''\
  </tbody>
</table>
  '''
  
  output.js.append('$("#%s").treeTable();' % id)
  
  return output


def Accordion(id, content_list, options=None, data=None, cookies=None, headers=None):
  """content_list is list of tuples (string,string): (title, content)"""
  output = Output()
  
  if options == None:
    options = {}
  
  # Create the opening DIV
  output += '<div id="%s" class="accordion">\n' % id
  
  # Create the tab row entries
  for count in range(0, len(content_list)):
    content = content_list[count]
    
    # Get the section labels, if we have them
    if 'labels' in options:
      output += '<h3><a href="#">%s</a></h3>\n' % options['labels'][count]
    else:
      output += '<h3><a href="#">%s</a></h3>\n' % count
    
    # Output the content
    output += '<div>\n'
    output += str(content)
    output += '</div>\n' 

  # Create the closing DIV
  output += '</div>\n'

  # This JS is needed to product this tab
  output.js.append("$('#%s').accordion('destroy'); $('#%s').accordion({fillSpace:true});" % (id, id))
  
  ## Specify all the tabs we need to collect to save cookies before reloading
  ##   any data that may reload the tabs
  #output.js.append('sections["%s"] = true;' % id)
  
  return output


def PopUp(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output(js_include=["js/jquery.BubblePopup-1.1.min.js"])

  # Render the script to put a popup over the specified Tag ID
  output += '''
  <script>
  $("#%s").SetBubblePopup({
    //bubbleAlign: 'center',
    //distanceFromTarget: 450,
    //hideTail: true,
    innerHtml: '%s'
  });
  </script>
  ''' % (id, content)
  
  return output


def Grid(id, content_dict, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  return output


def Layout(id, content_dict, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  return output


def Calendar(id, content_dict, options=None, data=None, cookies=None, headers=None):
  """content is dict of dates"""
  output = Output()
  
  return output


def CalendarRange(id, content_dict, options=None, data=None, cookies=None, headers=None):
  """content is dict of dates"""
  output = Output()
  
  return output


def TimeSelector(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  return output


def Menu(id, content, options=None, data=None, cookies=None, headers=None):
  """Menu"""
  if options == None:
    options = {}
  
  output = Output()
  
  # Get the menu button label
  if not options or 'label' not in options:
    name = 'UNNAMED'
  else:
    name = options['label']
  
  output += '''
<a tabindex="0" href="#" class="fg-button fg-button-icon-right ui-widget ui-state-default ui-corner-all" id="%s"><span class="ui-icon ui-icon-triangle-1-s"></span>%s</a>
<div id="%s_content" class="hidden">
<ul class="fg-menu">\n''' % (id, name, id)

  for item in content:
  	output += '<li class="fg-menu"><a href="#">%s</a></li>\n' % item
  
  output += '''
</ul>
</div>
  '''
  
  menu_prep_js = '''
$('.fg-button').hover(
  function(){ $(this).removeClass('ui-state-default').addClass('ui-state-focus'); },
  function(){ $(this).removeClass('ui-state-focus').addClass('ui-state-default'); }
);
  '''
  output.js.append(menu_prep_js)
  
  menu_js = '''
$('#%s').menu({ 
  content: $('#%s').next().html(), // grab content from this page
  showSpeed: 400,
  selectFunction: "%s"
});
  ''' % (id, id, options.get('function', 'alert')) # If no function, just alert
  output.js.append(menu_js)
  
  return output


def MenuVertical(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  return output


def MenuContext(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  return output


def Slider(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  return output


def ThemeRoller(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  output.css_include.append('http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/themes/base/ui.all.css')
  
  output.js.append("$('#%s').themeswitcher();" % id)
  
  output += '''
    <script type="text/javascript"
      src="http://jqueryui.com/themeroller/themeswitchertool/">
    </script>
    <div id="%s"></div>
  ''' % id
  
  return output


def MultiList(id, content, options=None, data=None, cookies=None, headers=None):
  """TODO(g): Change all references to this name, which is the jQuery UI Plugin
      Author's name for the widget.  Add him to credits, and provide URL.
  """
  return ListSelectAndOrder(id, content, options=options, data=data, cookies=cookies, headers=headers)


def ListSelectAndOrder(id, content, options=None, data=None, cookies=None, headers=None):
  """Creates a 2 column list selection.  The left column is the selected list,
  and can also be ordered.  The right column is the total possible list.
  
  Content is a tuple of lists (total_list, selected_list).
  
  Project Demo URL: http://michael.github.com/multiselect
  """
  output = Output()
  
  # Required for the MultiSelect project to work
  output.js_include.append("js/plugins/localisation/jquery.localisation-min.js")
  output.js_include.append("js/plugins/scrollTo/jquery.scrollTo-min.js")
  output.js_include.append("js/ui.multiselect.js")
  
  # CSS needed
  output.css_include.append("css/common.css")
  output.css_include.append("css/ui.multiselect.css")
  
  # JS needed to instantiate
  #output.js.append("$.localise('ui-multiselect', {/*language: 'en',*/ path: 'js/locale/'});")
  output.js.append('$("#%s").multiselect();' % id)

  # Add HTML
  output += '  <select id="%s" class="multiselect" multiple="multiple" name="%s[]">\n' % (id, id)
  
  # Get our lists from the content
  #TODO(g): Allow different values than labels...
  (total_list, selected_list) = content
  
  for item in total_list:
    if item in selected_list:
      output += '    <option value="%s" selected="selected">%s</option>\n' % (item, item)
    else:
      output += '    <option value="%s">%s</option>\n' % (item, item)
  
  output += '  </select>\n'
  
  return output


def Dialog(id, content, options=None, data=None, cookies=None, headers=None):
  output = Output()
  
  if options == None:
    options = {}
  
  title = options.get('title', 'Dialog')
  width = options.get('width', 600)
  auto_open = options.get('open', True)
  if auto_open:
    auto_open_str = "$('#%s').dialog('open');" % id
  else:
    auto_open_str = ''
  
  
  if options.get('modal', False):
    modal = 'true'
  else:
    modal = 'false'
  
  # The dialog widget HTML content
  output += '''
<div id="%s" title="%s">
%s
</div>
  ''' % (id, title, content)
  
  # Add the Javascript to initialize the dialog widget
  output += '''
  <script>
  // Destroy it first...
  $('#%s').dialog('destroy');
  
  // Dialog			
  $('#%s').dialog({
    autoOpen: false,
    width: %s,
    modal: %s,
    buttons: {
      "Cancel": function() { 
        $(this).dialog("close"); 
      }, 
    }
  });
  
  %s
  </script>
  ''' % (id, id, width, modal, auto_open_str)
  
  if auto_open:
    output.js.append("$('#%s').dialog('open');" % id)
  
  return output


def Dialog_Ok(id, content, options=None, data=None, cookies=None, headers=None):
  """Just like a normal Dialog() box, but this has an OK button, and will
  run a JS function if Ok is clicked.  It is not meant to do anything but
  prompt the usade with a status message (content=HTML string) and then
  call the JS function (in options['function']) if OK is clicked.
  """
  output = Output()
  
  if options == None:
    options = {}
  
  title = options.get('title', 'Dialog')
  width = options.get('width', 600)
  auto_open = options.get('open', True)
  if auto_open:
    auto_open_str = "$('#%s').dialog('open');" % id
  else:
    auto_open_str = ''
  
  
  if options.get('modal', False):
    modal = 'true'
  else:
    modal = 'false'
  
  # The dialog widget HTML content
  output += '''
<div id="%s" title="%s">
%s
</div>
  ''' % (id, title, content)
  
  # Add the Javascript to initialize the dialog widget
  output += '''
  <script>
  // Destroy it first...
  $('#%s').dialog('destroy');
  
  // Dialog			
  $('#%s').dialog({
    autoOpen: false,
    width: %s,
    modal: %s,
    buttons: {
      "Ok": function() { 
        %s
        $(this).dialog("close"); 
      }, 
      "Cancel": function() { 
        $(this).dialog("close"); 
      }, 
    }
  });
  
  %s
  </script>
  ''' % (id, id, width, modal, options.get('function', ''), auto_open_str)
  
  if auto_open:
    output.js.append("$('#%s').dialog('open');" % id)
  
  return output


def FieldSet(id, content, options=None, data=None, cookies=None, headers=None):
  """Renders a form, field sets, and Ajax controls to send RPC to the server.
  
  content: [{'Fieldset Label':[{'input_field_key':{'label':'Field Label', 'default':'Something', 'type':'text'}}]}]
  """
  
  output = Output()
  
  if options == None:
    options = {}
  
  method = options.get('action', '')
  action = options.get('method', 'post')
  
  # Open Form
  output += '''
  <form id="%s" action="%s" method="%s"> 
  ''' % (id, action, method)
  
  # Even/Odd fieldset counter
  fieldset_count = 0
  
  # Loop through our fieldset items
  for fieldset_item in content:
    for fieldset_key in fieldset_item:
      # Create alternating field sets, if the CSS is available
      fieldset_count += 1
      if fieldset_count % 2 == 1:
        fieldset_alt = ''
      else:
        fieldset_alt = ' class="alt"'
      
      # Open Field Set
      output += '''
  <fieldset>
    <legend><span>%s</span></legend>  
    <ol>
      ''' % fieldset_key
      
      # Loop through the inputs and labels in our fieldset
      for input_item in fieldset_item[fieldset_key]:
        for input_name in input_item:
          input_data = input_item[input_name]
          
          input_id = '%s_%s' % (id, input_name)
          input_label = input_data.get('label', input_name)
          input_type = input_data.get('type', 'text')
          input_default = input_data.get('default', '')
          input_disabled = input_data.get('disabled', False)
          
          # If this is hidden type, show the value, unless hide=True 
          if input_type == 'hidden':
            hidden_text = input_default
          else:
            hidden_text = ''
          
          # If this is disabled
          if input_disabled:
            disabled_text = 'disabled="disabled"'
          else:
            disabled_text = ''
          
          # Sizing: prepare
          if input_type == 'textarea':
            cols = input_data.get('cols', 60)
            rows = input_data.get('rows', 4)
            size_text = ' cols="%s" rows="%s"' % (cols, rows)
          elif 'size' in input_data:
            size_text = 'size="%s"' % input_data['size']
          else:
            size_text = ''
          
          
          # If we have a helper widget to select this data (file, calendar,
          #   range picker, color picker, etc)
          if 'select_widget' in input_data:
            #TODO(g): Need to do anything else here?  Not sure...
            select_widget = '<br>%s\n' % input_data['select_widget']
          else:
            select_widget = ''
          
          # If we have an input info statement, add it to the end
          #TODO(g): Do this with it's own data, not tacked on to select_widget
          if 'info' in input_data:
            select_widget += '<div style="margin-left: 11em;">%s</div>\n' % input_data['info']
          
          # If we are not hiding this row
          if input_type == 'textarea':
            output += '''
        <li>  
        <label for="%s">%s:</label>  
        <textarea id="%s" name="%s" class="%s" type="%s" style="margin-left:11em;" %s %s/>%s</textarea>
        %s
        %s
        </li>
          ''' % (input_name, input_label, id, input_name, input_type, input_type,
                 disabled_text, size_text, input_default, hidden_text, select_widget)
          
          # Else, If we are rendering a Checkbox input
          elif input_type == 'checkbox':
            # If this item should be checked, tag it
            if input_default:
              checked = 'checked'
            else:
              checked = ''
            
            output += '''
        <li>  
        <label for="%s">%s:</label>  
        <input id="%s" name="%s" class="%s" type="%s" %s %s %s/>
        %s
        %s
        </li>
          ''' % (input_name, input_label, id, input_name, input_type, input_type,
                 checked, disabled_text, size_text, hidden_text, select_widget)
          
          # Else, if this is a normal non-hidden input
          elif not input_data.get('hide', False):
            # Output our item
            output += '''
        <li>  
        <label for="%s">%s:</label>  
        <input id="%s" name="%s" class="%s" type="%s" value="%s" %s %s/>
        %s
        %s
        </li>
          ''' % (input_name, input_label, id, input_name, input_type, input_type,
                 input_default, disabled_text, size_text, hidden_text, select_widget)
          
          # Else, we are hiding this row, so only output the hidden input field
          else:
            output += '''
        <input id="%s" name="%s" class="%s" type="%s" value="%s" %s %s/>
          ''' % (id, input_name, input_type, input_type,
                 input_default, disabled_text, size_text)
        
      # Close Field Set
      output += '''
      </ol>  
    </fieldset>
    '''

  submit_label= options.get('submit', 'Submit')

  # Submit button for all Field Sets in Form
  output += '''
  <!-- Local button -->
  <fieldset class="submit">  
  <input class="submit" type="submit" value="%s" />  
  </fieldset>
  ''' % submit_label

  # Close Form
  output += '''
</form>
  '''

  # Get our RPC and JS functions
  rpc_function = options['rpc']
  js_success_function = options['js_function']

  # If we want to pass args with the RPC function, add the data (type=dict)
  if 'rpc_args' in options:
    data_str = """, 'data':%s""" % str(options['rpc_args'])
  else:
    data_str = ''

  # Initialize ajaxForm to process fields
  output += '''
<script>
$("#%s").ajaxForm({
  url: 'rpc/%s',
  dataType: 'json',
  success: %s
  %s
  });
</script>
  ''' % (id, rpc_function, js_success_function, data_str)
  
  return output


def CodeHighlight(id, content, options=None, data=None, cookies=None, headers=None):
  """Outputs code highlight.
  
  Args:
    content: string, path to code to highlight
  """
  output = Output()
  
  if options == None:
    options = {}
  
  
  # Get options
  code_type = options.get('code', 'python')
  style = options.get('style', 'vs')
  
  # Get the lexer and formatter
  lexer = pygments.lexers.get_lexer_by_name(code_type, stripall=True)
  formatter = pygments.formatters.HtmlFormatter(linenos=True, style=style)
  
  # Add the CSS
  output += '<style>%s</style>\n' % formatter.get_style_defs('.highlight')
  
  # Add the Highlighted code
  highlighted = pygments.highlight(open(content).read(), lexer, formatter)
  output += '%s\n' % highlighted
  
  return output


def MatchRegexFiles(path_regex):
  """Returns a dictionary of matchs based on the regex and file names.
  
  TODO(g): CWD is critical here.  Duh!
  """
  dirs = {}
  
  #TODO(g): CWD is not always where we want to search.  Fix this up.
  items = os.walk('.')
  for (path, path_dirs, files) in items:
    # Crop the "./" from the beginning of all paths, worthless
    path = path[2:]
    
    matched_files = []
    
    # Loop over the files and test
    for filename in files:
      filepath = '%s/%s' % (path, filename)
      regex = '^(%s)$' % path_regex
      found = re.findall(regex, filepath)
      #print 'MatchRegex: %s: %s: %s' % (filepath, regex, found)
      if found:
        matched_files.append(filename)
    
    # If we matched any, add this directory, and all the files
    if matched_files:
      # Break down our path and ensure all the directionaries are present
      (dir_chunks) = path.split('/')
      # Start cur_dir pointing at the root dirs dict
      cur_dir = dirs
      for dir_chunk in dir_chunks:
        #print 'Dir: %s: %s: %s' % (path, dir_chunk, cur_dir)
        # If this directory chunk doesn't exist yet, create it
        if dir_chunk not in cur_dir:
          cur_dir[dir_chunk] = {}
        
        # Change so this is current
        cur_dir = cur_dir[dir_chunk]
      
      # Now that we've ensured all the parent directories exist, and we have
      #   a reference to the current directory these files are in, add them as
      #   entries
      #TODO(g): Better things to put in here?  Stat info?  Whats a good default?
      for matched_file in matched_files:
        cur_dir[matched_file] = '%s/%s' % (path, matched_file)
  
  return dirs


def FileTableTree(id, content, options=None, data=None, cookies=None, headers=None):
  """Prints a Tree Table for the file system, matched against content regex.
  
  Options input_fieldset and input_name allow specification of an INPUT value
  to fill in, with the selection of this tree item.
  
  TODO(g): Add "rpc" option as well, which will RPC this function.
  TODO(g): Dynamic RPC: "Dynamic:path/to/script.py"
  """
  output = Output()
  
  if options == None:
    options = {}
  
  # Directory dict-in-dict structure
  #TODO(g): Walk the directory tree, find matches for the content regex, and
  #   add them to the dict tree, for rendering in TableTree
  #dirs = {'Test':{'Bonk':'Zonk'}}
  dirs = MatchRegexFiles(content)
  
  
  # Get all the items in a flat list, with their parents marked, so they can
  #   be displayed in a non-flat hierarchy
  tree_items = _GetTreeItems(dirs)
  
  output += '''
<table id="%s" class="ui-widget ui-widget-content">
  <thead class="ui-widget-header">
    <tr>
      <th>Path</th>
    </tr>
  </thead>
  <tbody class="ui-widget-content">
  ''' % id
  
  # Add all our tree items
  for item in tree_items:
    item_id = item['id']
    item_child = ''
    if 'parent' in item:
      item_child = 'class="child-of-%s"' % item['parent']
    icon = item.get('icon', 'file') # Default as file, not folder.  Improve this
    key = item['key']
    kind = item['kind']
    value = item['value']
    
    if 'input_fieldset' in options and 'input_name' in options:
      onClick = '''onClick="$('#%s input[name=%s]').each(function(n,element){$(element).val('%s');});"''' % (options['input_fieldset'], options['input_name'], value)
    else:
      onClick = ''
    
    output += '''
    <tr id="%s" %s>
      <td class="initial"><span class="%s" %s>%s</span></td>
    </tr>
    ''' % (item_id, item_child, icon, onClick, key)

  output += '''\
  </tbody>
</table>
  '''
  
  output.js.append('$("#%s").treeTable({"initialState":"expanded"});' % id)
    
  return output


def SelectMenu(id, content, options=None, data=None, cookies=None, headers=None):
  """A select menu, with basic popup style.  Simple.  content=list of strings.
  """
  output = Output()
  
  if options == None:
    options = {}
  
  # If there is a select function, set it
  if 'select' in options:
    select = 'onselect="%s"' % options['select']
  else:
    select = ''
  
  # Create the selectmenu select tag
  output += '''
    <select name="%s" id="%s" %s>
  ''' % (id, id, select)
  
  # Add the content items
  for item in content:
    # If this item is selected (optional)
    if item == options.get('selected', None):
      output += '''
        <option value="%s" selected="selected">%s</option>
      ''' % (item, item)
    
    # Else, this item is not selected
    else:
      output += '''
        <option value="%s">%s</option>
      ''' % (item, item)
  
  # Close
  output += '''
    </select>
  '''

  # Initialize the selectmenu
  output.js.append("$('#%s').selectmenu('destroy'); $('#%s').selectmenu()" % (id, id))
  
  return output
  
  
def Layout(id, content, options=None, data=None, cookies=None, headers=None):
  """Layout: 5 cells: center, north, south, east, west
  
  Layout is completely automated.  If the key is filled in, the area is created.
  """
  output = Output()
  
  if options == None:
    options = {}
  
  # Open the layout
  output += '''
  <div id="%s" class="layout {layout: {type: 'border', hgap: 3, vgap: 3}}">
  ''' % id
  
  # Selectively create the areas
  if content.get('north', False):
    output += '\n<div class="north">\n%s\n</div>\n' % content['north']
  
  if content.get('center', False):
    output += '\n<div class="center">\n%s\n</div>\n' % content['center']
  
  if content.get('west', False):
    output += '\n<div class="west">\n%s\n</div>\n' % content['west']
  
  if content.get('east', False):
    output += '\n<div class="east">\n%s\n</div>\n' % content['east']
  
  if content.get('south', False):
    output += '\n<div class="south">\n%s\n</div>\n' % content['south']
  
  # Close the layout
  output += '''
  </div>
  '''

  ##TODO(g): Inner/outer and other options...
  ##output.js.append("$('#%s').layout();" % id)
  #js = '''
  #  jQuery(function($)
  #  {
  #    var container = $('#%s');
  #    
  #    function relayout() {
  #      container.layout({resize: false});
  #    }
  #    relayout();
  #    
  #    $(window).resize(relayout);
  #  });
  #''' % id
  
  return output


