# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Roberto Longobardi - seccanj@gmail.com, Marco Cipriani
#

import re

from operator import itemgetter

from genshi.builder import tag

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.ticket.query import Query, TicketQueryMacro
from trac.web.chrome import add_script
from trac.wiki.macros import WikiMacroBase
from trac.wiki.api import WikiSystem, parse_args, IWikiMacroProvider
from trac.wiki.model import WikiPage


class TicketTreeMacro(WikiMacroBase):
    implements(IWikiMacroProvider)
    """Display a tree of tickets.

    Usage:

    {{{
    [[TicketTree(query)]]
    }}}

    See tags documentation for the query syntax.
    """
    def expand_macro(self, formatter, name, content):
        if not content:
            content= ''
        add_script(formatter.req, 'tickettree/js/tickettree.js') 
        return _render_build_ticket_tree(self.env, formatter.req, content)
        

class TicketTreeLimitedMacro(WikiMacroBase):
    implements(IWikiMacroProvider)
    """Display a list of catalogs.

    Usage:

    {{{
    [[TicketTreeLimited(query)]]
    }}}

    See tags documentation for the query syntax.
    """
    def expand_macro(self, formatter, name, content):
        if not content:
            content= ''
        add_script(formatter.req, 'tickettree/js/tickettree.js') 
        return _render_build_ticket_tree_limited(self.env, formatter.req, content)
        
    
def _render_build_ticket_tree(env,req,content):
    filter = ''
    if "filter" in req.args:
        filter = req.args["filter"]
        
    query_string = ''
    argv, kwargs = parse_args(content, strict=False)
    if len(argv) > 0 and not 'format' in kwargs: 
        kwargs['format'] = argv[0]
    kwargs['order'] = 'summary'
    kwargs['max'] = '0' 
    kwargs['col'] = 'summary'
    query_string = '&'.join(['%s=%s' % item for item in kwargs.iteritems()])
    query = Query.from_string(env, query_string)
    tickets = query.execute(req)
    components = {'name': 'root', 'childrenC': {},'childrenT': {}, 'tot': 0, 'totC': 0}
    for t in tickets:
        summ=t.get("summary")
        id=t.get("id")

        tokens = summ.split(" - ")
        parent = components
        ltok = len(tokens)
        count = 1;
        for tk in tokens:
            tc = tk
            if (count != ltok & ltok > 1):
                comp = {}
                if (tc not in parent['childrenC']):
                    comp = {'name': tc, 'childrenC': {},'childrenT': {}, 'tot': 0, 'totC': 0, 'parent': parent}
                    parent['childrenC'][tc]=comp
                else:
                    comp = parent['childrenC'][tc]
                parent = comp
            else:
                parent['childrenT'][summ]={'id':id, 'summary':summ, 'status': t.get("status")}
                compLoop = parent
                while (True):
                    compLoop['tot']+=1
                    if ('parent' in compLoop):
                        compLoop = compLoop['parent']
                    else:
                        break
                compLoop = parent
                if  (t.get("status")=="closed"):
                    while (True):
                        compLoop['totC']+=1
                        if ('parent' in compLoop):
                            compLoop = compLoop['parent']
                        else:
                            break
            count+=1
    
    text = '<form method="GET" action="'+req.base_url+req.path_info+'">'
    text +='<div style="padding: 0px 0px 10px 10px">Find: <input id="filter" name="filter" type="text" size="40"  value="'+filter+'" onkeyup="checkFilter()"/><input name="ricarica" type="submit" value="Refresh"/></div>'
    text +='</form>'
    text +='<div style="font-size: 0.8em;padding-left: 10px"><a style="margin-right: 10px" onclick="toggleAll(true)" href="javascript:void(0)">Expand all</a><a onclick="toggleAll(false)" href="javascript:void(0)">Collapse all</a></div>';
    text +='<div id="ticketContainer" style="display: none">'
    ind = {'count': 0}
    text += _render_data(components,len(tickets),ind,0)
    text +='</div>'
    return text
    

def _render_data(component,tot,ind,level,path=""):
    data = component
    text = ''
    if (level == 0):
        data = component['childrenC']
        text +='<ul style="list-style: none;">';        
    keyList = data.keys()
    sortedList = sorted(keyList)
    for x in sortedList:
        ind["count"]+=1
        text+='<li style="font-weight: normal">'
        comp = data[x]
        fullpath = path+x+" - "
        if ('childrenC' in comp):
            subcData=comp['childrenC']
            text+='<span name="toggable" style="cursor: pointer" id="b_'+str(ind["count"])+'" onclick="toggle(\'b_'+str(ind["count"])+'\')"><span style="font-family: courier">+</span> '+x+' ('+str(comp["tot"]-comp["totC"])+' open, '+str(comp["totC"])+' closed)</span><span style="cursor: pointer;color: #BB0000;margin-left: 10px;font-size: 0.8em" onclick="window.open(\'../newticket?summary='+fullpath.replace("'","&#146;")+'[summary]\')">open ticket</span>'
            text +='<ul id="b_'+str(ind["count"])+'_list" style="display:none;list-style: none;">';
            ind["count"]+=1
            text+=_render_data(subcData,tot,ind,level+1,fullpath)
            if ('childrenT' in comp):            
                mtData=comp['childrenT']
                text+=_get_tickets(mtData)
        text+='</ul>'
        text+='</li>'
    if (level == 0):
        if ('childrenT' in component):            
            cmtData=component['childrenT']
            text+=_get_tickets(cmtData)
        text+='</ul>'        
    return text
                

def _get_tickets(data): 
    text=''
    valueList = data.values()
    sortedList = sorted(valueList,key=itemgetter('status', 'id'))
    #lambda ticket: ticket["status"]+"_"+str(ticket["id"]))
    for tick in sortedList:
        #tick = data[x]
        style = ''
        if tick["status"] == "closed":
            style='text-decoration:line-through;'
        text+="<li style='font-weight: normal'><a target='_blank' style='"+style+"' href='../ticket/"+str(tick["id"])+"' >#"+str(tick['id'])+"&nbsp;"+tick['summary']+"&nbsp;<span style='font-size: 0.8em'>["+tick['status']+"]</span></a></li>"
    return text
    
    
def _render_build_ticket_tree_limited(env,req,content):
    filter = ''
    if "filter" in req.args:
        filter = req.args["filter"]
        
    query_string = ''
    argv, kwargs = parse_args(content, strict=False)
    if len(argv) > 0 and not 'format' in kwargs: 
        kwargs['format'] = argv[0]
    kwargs['order'] = 'summary'
    kwargs['max'] = '0' 
    kwargs['col'] = 'summary'
    query_string = '&'.join(['%s=%s' % item for item in kwargs.iteritems()])
    query = Query.from_string(env, query_string)
    tickets = query.execute(req)
    components = {};

    for t in tickets:
        summ=t.get("summary")
        id=t.get("id")
        ss=summ.partition(" - ")
        tcc1 = ss[0]
        ss2=ss[2].partition(" - ")
        if ss2[1] != "":
            tcc2 = ss2[0]
        else:
            tcc2 = ''
        comp = {}
        if (tcc1 not in components):
            comp = {'name': tcc1, 'childrenC': {},'childrenT': {}, 'tot': 0, 'totC': 0}
            components[tcc1]=comp
        else:
            comp = components[tcc1]
        if (tcc2 != ''):
            if (tcc2 not in comp['childrenC']):
                subcom = {'name': tcc2, 'childrenT': {}, 'tot': 0, 'totC': 0}
                comp['childrenC'][tcc2]=subcom
            else:
                subcom = comp['childrenC'][tcc2]   
            subcom['childrenT'][summ]={'id':id, 'summary':summ, 'status': t.get("status")}
            subcom['tot']+=1
            comp['tot']+=1
            if  (t.get("status")=="closed"):
                subcom['totC']+=1
                comp['totC']+=1
        else:
            comp['childrenT'][summ]={'id':id, 'summary':summ, 'status': t.get("status")}
            comp['tot']+=1
            if  (t.get("status")=="closed"):
                comp['totC']+=1

    text = get_script()
    text +='<div style="padding: 0px 0px 10px 10px">Find: <input type="text" size="40" onkeyup="highlight(this.value)" value="'+filter+'"/></div>'
    text +='<div style="font-size: 0.8em;padding-left: 10px"><a style="margin-right: 10px" onclick="toggleAll(true)" href="javascript:void(0)">Expand all</a><a onclick="toggleAll(false)" href="javascript:void(0)">Collapse all</a></div>';
    text +='<div id="ticketContainer">'
    text += _render_data_limited(components,len(tickets),0)
    text +='</div>'
    return text

def _render_data_limited(data,tot,ind):
    
    text = ''
    text +='<ul style="list-style: none;">';
    keyList = data.keys()
    sortedList = sorted(keyList)
    for x in sortedList:
        text+='<li style="font-weight: normal">'
        ind+=1
        comp = data[x]
        if ('childrenC' in comp):
            subcData=comp['childrenC']
            mtData=comp['childrenT']
            text+='<span name="toggable" style="cursor: pointer" id="b_'+str(ind)+'" onclick="toggle(\'b_'+str(ind)+'\')"><span style="font-family: courier">+</span> '+x+' ('+str(comp["tot"]-comp["totC"])+' open, '+str(comp["totC"])+' closed)</span><span style="cursor: pointer;color: #BB0000;margin-left: 10px;font-size: 0.8em" onclick="window.open(\'../newticket?summary='+x+'%20-%20[summary]\')">open ticket</span>'
            keyList2 = subcData.keys()
            sortedList2 = sorted(keyList2)
            text +='<ul id="b_'+str(ind)+'_list" style="display:none;list-style: none;">';
            for x2 in sortedList2:
                text+='<li style="font-weight: normal">'
                ind+=1
                scomp = subcData[x2]
                tData=scomp['childrenT']
                text+='<span name="toggable" style="cursor: pointer" id="b_'+str(ind)+'" onclick="toggle(\'b_'+str(ind)+'\')"><span style="font-family: courier">+</span> '+x2+' ('+str(scomp["tot"]-scomp["totC"])+' open, '+str(scomp["totC"])+' closed)</span><span style="cursor: pointer;color: #BB0000;margin-left: 10px;font-size: 0.8em" onclick="window.open(\'../newticket?summary='+x+'%20-%20'+x2+'%20-%20[summary]\')">open ticket</span>'
                text +='<ul id="b_'+str(ind)+'_list" style="display:none;list-style: none;">';
                text+=_get_tickets(tData)
                text +='</ul>';
                text+='</li>'
            text+=_get_tickets(mtData)
            text+='</ul>'
    text+='</ul>'
    return text
