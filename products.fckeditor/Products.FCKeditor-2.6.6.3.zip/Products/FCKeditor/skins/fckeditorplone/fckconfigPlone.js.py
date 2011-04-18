## Script (Python) "fckconfigPlone.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title= fck custom config for Plone
##

request = context.REQUEST
field_name = request.get('field_name','')
macro="rich"
if field_name :
    try:
        field = context.schema[field_name]
    except:
        # some plone products (ex : PloneBoard) are using wysiwyg support without AT field
        field = None
    if field :
        widget = field.widget
        macro = widget.macro   
if macro == 'fckwidget':    
    return widget.getCustomConfig(context)

fckParams = context.getFck_params()

customConfig ="""FCKConfig.ToolbarStartExpanded	= %s;
FCKConfig.ToolbarSets["Custom"] = %s ;
FCKConfig.Keystrokes = %s ;
FCKConfig.FontFormats = 'p;div;pre;code;address;h2;h3;h4;h5;h6' ;
FCKConfig.StylesXmlPath = FCKConfig.EditorPath + 'fckstyles_plone.xml' ;
FCKConfig.EditorAreaCSS		= %s ;
"""  %(fckParams['start_expanded'] and 'true' or 'false',
       fckParams['fck_custom_toolbar'],
       fckParams['keyboard_customkeystrokes'],
       fckParams['fck_style'])

return customConfig
