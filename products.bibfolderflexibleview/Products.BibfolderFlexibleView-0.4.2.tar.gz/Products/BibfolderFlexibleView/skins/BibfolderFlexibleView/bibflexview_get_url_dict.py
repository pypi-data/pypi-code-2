## Script (Python) "bibflexview_get_url_dict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=prop_src, objlist, REQUEST=None
##title=
##

# nehme eine liste von listen von objekten, gebe ein dictionary zurueck, jeweils mit "id: [{id:..., title:.., url:..., ico:...}"

def ip_in_range(prop_src, REQUEST):
# das ist wahrscheinlich nich hundert prozent narrensicher, also nur fuer nicht wirklich sicherheits-rlevante dinge benutzen
    HU_range = prop_src.ao_ip_check_range
    return (REQUEST.has_key('HTTP_X_FORWARDED_FOR')) and (HU_range in REQUEST['HTTP_X_FORWARDED_FOR']) or (HU_range in REQUEST['REMOTE_ADDR'])

# XXX alternativ: id: obj zurueckgeben, damit endnutzer flexibler damit umgehen koennen? jetzt, wo wirs nich mehr direkt im
# template verwursten?
# XXX konfigurierbar machen: filesufxs, pdf-ausnahme
# XXX in diesem sinne vllt als skript-objekt, damit customizable
res = {}

if prop_src.use_ao_ip_check and REQUEST: is_hu_ip = ip_in_range(prop_src, REQUEST)
else: is_hu_ip = True

filesufxs = ('.pdf', '.jpg', '.jpeg', '.ps', '.mov', '.mpg', '.mpeg', '.doc', '.xls', '.ods', '.odt', '.htm', '.html')
cat = context.portal_catalog

for obj in objlist:
    # XXX getURL()
    url = obj.Type == 'Link' and obj.getRemoteUrl or obj.getURL() 
    
    priv = ''
    if prop_src.ao_show_priv and not context.portal_bibliography_flexible_view.is_get_object_authorized(obj):
        priv = 'unauthorized'
    
    # intern?
    # XXX diese IP-Kruecke sollte wahrscheins raus
    if not ((prop_src.ao_ip_check_keyword in url) and (not is_hu_ip)):
        key = obj.id
        for sufx in filesufxs:
            if key.endswith(sufx): 
                key = key.split('.',1)[0]
                break
        if obj.Title: title = obj.Title
        else: title = obj.id
# hier sonderbehandlung von pdfs - wenn fuer die wie fuer alle anderen der Dateiname
# angezeigt werden soll, die folgende zeile entfernen. sollte man vielleicht lang-
# fristig eleganter/allgemeiner regeln
        if title.endswith('pdf'): title = 'Download as pdf-file'

        #od = {'id': obj.id, 'title': title, 'url': url, 'ico': obj.getIcon}
        od = {'id': obj.id, 'title':  title, 'url': url, 'ico': obj.getIcon, 'priv': priv}
        if res.has_key(key): res[key].append(od)
        else: res[key] = [od]
return res
