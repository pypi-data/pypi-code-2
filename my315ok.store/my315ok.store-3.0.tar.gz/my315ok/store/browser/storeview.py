from zope.interface import implements, Interface

from Products.Five import BrowserView
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from my315ok.store import storeMessageFactory as _


class IstoreView(Interface):
    """
    store view interface
    """

    def test():
        """ test method"""


class storeView(BrowserView):
    """
    store browser view
    """
    implements(IstoreView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    @memoize
    def prdt_images(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        sepath= '/'.join(context.getPhysicalPath()) 
        query = {'meta_type':('goods_image'),
                 'sort_on':'getObjPositionInParent',
                 'sort_order':'forward',
                 'review_state':'published',
                 'path':sepath,
                 }        
        sd = catalog(query)
        return sd
    @memoize
    def img_tag(self,fieldname="image",small="tile",preview="mini",large="large"):
        imglists = {}
        csmall = []
        cpreview = []
        clargelink = []
        imgviewurl = []
        imgobjs = self.prdt_images()
        num = len(imgobjs)
        if num > 0:            
            for i in imgobjs:
                jt = i.getObject()
                try:
                    fd = jt.getField(fieldname)
                    csmall.append(fd.tag(jt,scale=small))
                    cpreview.append(fd.tag(jt,scale=preview))
                    clargelink.append(jt.absolute_url() + "/" + fieldname + "_" + large)
                    imgviewurl.append(jt.absolute_url() + "/@@goods_image__view")
                except:
                    continue                
            
        imglists["small"] = csmall
        imglists["preview"] = cpreview
        imglists["large"] = clargelink
        imglists["imgurl"] = imgviewurl
        return imglists
    @memoize
    def img_fast_tag(self,fieldname="image",small="tile",preview="mini",large="large"):
#        import pdb
#        pdb.set_trace()
        imglists = {}
        csmall = []
#        cdsptxt = []
        corig = []
        cpreview = []
        clargelink = []
        imgviewurl = []
#        imgtitle = []
        imgobjs = self.prdt_images()
        num = len(imgobjs)
        if num > 0:            
            for i in imgobjs:            
                try:
#                    base = self.request['ACTUAL_URL']
#                    id = i.getId()
                    base = i.getURL()
                    tl = i.Title
#                    dsp = i.Description
#                    try:
#                        dsplist = dsp.split(",")
#                    except:
#                        dsplist = dsp.split("u'，'")
#                    k = len(dsplist)
#                    sp1 = "<span>"
#                    sp2 = "</span>"
                          
                    surl = base + "/" + fieldname + "_" + small
                    ourl = base + "/" + fieldname 
                    purl = base + "/" + fieldname + "_" + preview
                    lurl = base + "/" + fieldname + "_" + large 
                    simg = "<img src='%s' alt='%s' title='%s' />" % (surl,tl,tl)
                    oimg = "<img src='%s' alt='%s' title='%s' />" % (ourl,tl,tl)
                    pimg = "<img src='%s' alt='%s' title='%s' />" % (purl,tl,tl)
#                    dsptxt = "<div class='rollzonetxt'>"
#                    dsptxtend = "</div>"
#                    for j in range(k):
#                        dsptxt = dsptxt + sp1 + dsplist[j] + sp2
#                    limg = "<img src='%s' alt='%s' title='%s' />" % (lurl,tl,tl)

    
                    imgobjurl = base + "/@@goods_image__view"
#                    dsptxt = dsptxt + dsptxtend
#                    cdsptxt.append(dsptxt)                   
                    csmall.append(simg)
                    corig.append(oimg)
                    cpreview.append(pimg)
                    clargelink.append(lurl)
                    imgviewurl.append(imgobjurl)
#                    imgtitle.append(tl)
                except:
                    continue                
            
        imglists["small"] = csmall
#        imglists["dsptxt"] = cdsptxt
        imglists["orig"] = corig
        imglists["preview"] = cpreview
        imglists["large"] = clargelink
        imglists["imgurl"] = imgviewurl
#        imglists["title"] = imgtitle
        return imglists
    
    @memoize
    def barview(self,scale="large",multiline=False):
        "genarator bars html"
        headstr =''
        bodystr = ''
#        items = self.imgitems(scale=scale)
        items = self.imgitems_fast(scale=scale)
        try:
            lenth = len(items['titl'])
            if bool(multiline):
                for i in range(lenth):
                    headstr = headstr + '<link url="%s" /><title text="%s"> </title>' % (items['url'][i],items['titl'][i])
                    bodystr = bodystr + '<div class="banner"><a href="%s"><img src="%s" alt="%s" />%s</a></div>' % (items['url'][i],items['src'][i],items['titl'][i],items['txt'][i])

                
            else:
                for i in range(lenth):
                    headstr = headstr + '<link url="%s" /><title text="%s"> </title>' % (items['url'][i],items['titl'][i])
                    bodystr = bodystr + '<div class="banner"><a href="%s"><img src="%s" alt="%s" /></a></div>' % (items['url'][i],items['src'][i],items['titl'][i])

                
            #                bodystr = bodystr + '<banner><ad><a href="%s"><img src="%s" alt="%s" /></a></ad></banner>' % (items['url'][i],items['src'][i],items['titl'][i])
        except:
            pass
        bars = {}
        bars['hstr'] = headstr
        bars['bstr'] = bodystr
        return bars
    
    @memoize
    def imgitems(self,scale="large"):
        brains = self.prdt_images()
        items = {}
        items['titl'] = []
        items['url'] = []
        items['src'] = []
        if scale == "orig":
            for bn in brains:
                obj = bn.getObject()
                items['titl'].append(obj.Title())
                items['url'].append(obj.getLink2())
                items['src'].append(obj.absolute_url() + "/image")          
            return items
            
        else:            
            for bn in brains:
                obj = bn.getObject()
                items['titl'].append(obj.Title())
                items['url'].append(obj.getLink2())
                items['src'].append(obj.absolute_url() + "/image_" + scale)          
            return items
                  
    def splittxt(self,dsp,tab):
        
        """ """
        if dsp == None:
            return None
        try:
            dsplist = dsp.split(tab)
        except:
            dsplist = dsp.split(",")
        k = len(dsplist)
        sp1 = "<span>"
        sp2 = "</span>"
        dsptxt = "<div class='rollzonetxt'>"
        dsptxtend = "</div>"
        for j in range(k):
            dsptxt = dsptxt + sp1 + dsplist[j] + sp2
            
        dsptxt = dsptxt + dsptxtend
        return dsptxt
        
                    
    @memoize
    def imgitems_fast(self,scale="large",tab=u"，"):
#        import pdb
#        pdb.set_trace()
        brains = self.prdt_images()
        items = {}
        items['titl'] = []
        items['url'] = []
        items['src'] = []
        items['txt'] = []
        if scale == "orig":
            for bn in brains:
#            obj = bn.getObject()
                base = bn.getURL()
                
                items['titl'].append(bn.Title)
                dsp = self.splittxt(bn.Description, tab)
                items['txt'].append(dsp)
                if type(bn.link2) =="Missing":
                    url = ""
                else:
                    url = bn.link2
                items['url'].append(url)
                items['src'].append(base + "/image")          
            return items
        else:
            
            for bn in brains:
#            obj = bn.getObject()
                base = bn.getURL()
                items['titl'].append(bn.Title)
                dsp = self.splittxt(bn.Description, tab)
                items['txt'].append(dsp)
                if type(bn.link2) =="Missing":
                    url = ""
                else:
                    url = bn.link2
                items['url'].append(url)
                items['src'].append(base + "/image_" + scale)          
            return items
    @memoize
    def swich_img(self):
        out = """
        jq("li.imgli").bind("mouseenter",function(){
        imgobj = jq(this).find('img');
        tit = imgobj.attr('alt');
        smsrc = imgobj.attr('src');
        bgsrc = smsrc.replace('_tile','_large');
        mdsrc = smsrc.replace('_tile','_mini');        
        newa="<a id='bigphoto' href='"+bgsrc+"' class='jqzoom' title='"+tit+"'><img src='"+mdsrc+"' alt='"+tit+"' /></a>";
        jq("#bigphoto").replaceWith(newa);
        jq(".jqzoom").jqzoom(); 
        })"""
        return out


        
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')
        return {'dummy': dummy}
