from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore import utils as cmfutils
from Products.Five.browser import pagetemplatefile
#from Products.Five.browser import absoluteurl


from collective.plone.gsxml.context import TarballExportContext
from collective.plone.gsxml.content import XMLContentFSExporter


from jw.tustep import tustepMessageFactory as _
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter 
import urllib
import xml.dom.minidom as dom
import os
import shutil
import re
import webbrowser
import xmlrpclib 
import codecs

class ITustepFormSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    @interface.invariant
    def invariant_url(input):
        pass
	# Check input values example:
	# if input.name != 'value':
        #    raise interface.Invalid(_(u"Some error occurred !"))

class TustepForm(formbase.PageForm):
    form_fields = form.FormFields(ITustepFormSchema)
    label = _(u'Erstellen von PDF')
    description = _(u'Durch anklicken von "PDF generieren" wird eine PDF-Datei vom aktuellen Dokument erzeugt.')
    result_template = pagetemplatefile.ZopeTwoPageTemplateFile('ergebnis.pt')

    @form.action('PDF generieren')
    def actionpdf(self, action, data):
        
        #-Jonas-Wagner------------------------------------------------------
        #Kontext-Prüfung
        #-------------------------------------------------------------------
        pfad = '/home/wagner/'          

        pstate = getMultiAdapter((self.context, self.request), name='plone_context_state')
        url = pstate.current_base_url()
        url = re.sub('/tustepform','',url)

        portal = getSite()

        #-Export-Test
        #-------------------------------------------------------------------
        export_context = TarballExportContext()
        exporter = XMLContentFSExporter(self.context)
        exporter.export(export_context, "structure", True)


        #archive = export_context.getArchiveStream()
        #archive.seek(0)

        
        
        file = export_context.getArchiveStream()  
        name = export_context.getArchiveFilename()  
        size = export_context.getArchiveSize()

        ausgabe = open(pfad + 'archiv', "w") 
        ausgabe.write(file.getvalue()) 
        ausgabe.close()
        
        shutil.rmtree(pfad + 'structure')
        os.system('tar xf ' + pfad + 'archiv --directory=' + pfad)
        
        #Ab hier Aufbereitung der Archiv-Daten
        #--------------------------------------------------------------
        eigenname = re.sub(".*/", "", url)
        string_text = ""
        
        ausgabe = codecs.open(pfad + 'ymir.xml', "w", "utf8") 
        ausgabe.write("Vor der Verarbeitung der XML-Datei")
        ausgabe.close()

        # Verarbeitung der XML-Datei
        #--------------------------------------------------------------
        xml_datei = open(pfad + 'structure/' + eigenname + r'.xml', "r")
        xml_text = ""
        for line in xml_datei: 
            xml_text += line
        
        baum = dom.parseString(xml_text)
        
        eintraege = ["shorttitle", "histdatum", "stddatum", "histort"]

        divs = baum.lastChild.getElementsByTagName("cmf:type")
        for di in divs:
            text = re.sub("\A\s*", "", str(di.firstChild.data))
            text = re.sub("\s*\Z", "", text)
            string_text += "<type>" + text + "</type>\n"
        
        # Autorname
        #-------------------------------------------------------------
        divs = baum.lastChild.getElementsByTagName("dc:creator")
        for di in divs:
            text = re.sub("\A\s*", "", str(di.firstChild.data))
            text = re.sub("\s*\Z", "", text)
            text_fullname = portal.portal_membership.getMemberInfo(text)
            if text_fullname is not None:
                 string_text += "<ersteller>" + text_fullname['fullname'] + "</ersteller>\n"
            else:
                 string_text += "<ersteller>" + text + "</ersteller>\n"


        divs = baum.lastChild.getElementsByTagName("field")
        for di in divs:
            for eintrag in eintraege:
                if di.getAttribute("name") == eintrag:
                     
                    str_eintrag = "<" + eintrag + ">" + str(di.firstChild.data) + "</" + eintrag + ">" + '\n'
                    str_eintrag = re.sub("\n", "", str_eintrag)
                    str_eintrag = re.sub("\r", "", str_eintrag)
                    str_eintrag = re.sub("\t", "", str_eintrag)
                    str_eintrag = re.sub("\A\s*", "", str_eintrag)
                    str_eintrag = re.sub("\s*\Z", "", str_eintrag)
                    string_text += str(str_eintrag) + "\n"
                    
        ausgabe = codecs.open(pfad + 'ymir.xml', "w", "utf8") 
        ausgabe.write(string_text)
        ausgabe.close()

      

        # Verarbeitung der .data-Dateien
        #--------------------------------------------------------------
        texttypen = ["untertitel", "fabstract", "description", "regest", "fundort", "druckort", "fachartikeltext", "originaltext", "text", "erlauterung", "uebetragung", "aboutauthors"]
        ausgabe = codecs.open(pfad + 'kontrolle.xml', "w", "utf8")
        for i in texttypen:
            #Versuch des Oeffnens der Dateien 
            text_name =  eigenname + r"." + i + r".data"
            try:
                datei = codecs.open(pfad + 'structure/' + text_name, encoding="utf8")
                text = datei.read()
                datei.close()
            
                text = text + "\n"

                #baum = dom.parsestring(text)
                #links = baum.lastChild.getElementsByTagName("a")
                #for i in links:
                    #baum.lastChild.removeChild(i)

                #text = baum.toxml()

                ausgabe.write(text)
                if re.search("\w", text):
                    text = re.sub("<!-- start content -->", "", text)
                    text = re.sub ("\s*<br.*?>\s*", "<br />xxxx", text)
                    text = re.sub ("xxxx", chr(10), text)
                    text = re.sub("\A\s*?", "", text, re.DOTALL)
                    text = re.sub("\s*?\Z", "", text, re.DOTALL)
                    text = re.sub("&nbsp;?", " ", text, re.DOTALL)
                    text = re.sub("&quot;?", '"', text, re.DOTALL)
                    text = re.sub("<script.*?/script>", "", text, re.DOTALL)
                    text = re.sub("<a.*?>", "", text, re.DOTALL)
                    text = re.sub("</a>", "", text, re.DOTALL)
                    text = re.sub("<ol.*?>", "", text, re.DOTALL)
                    text = re.sub("</ol>?", "", text, re.DOTALL)
                    text = re.sub("<b>", "<strong>", text, re.DOTALL)
                    text = re.sub("</b>", "</strong>", text, re.DOTALL)
                    text = re.sub("<i>", "<em>", text, re.DOTALL)
                    text = re.sub("</i>", "</em>", text, re.DOTALL)

                    
                    text = re.sub("&hellip;", "<punkte/>", text)
                    text = re.sub("&mdash;", "-", text)

                    # Ab hier Fussnotenarbeiten
                    #-----------------------------------------
                    fn_eintraege = re.findall("<li id=\"InsertNoteID_.*?</li>", text, re.DOTALL)
                    for fn_i in fn_eintraege:
                        fn_id = re.findall("(?<=InsertNoteID_)\d*", fn_i)[0]
                        fn_eintrag = re.findall("(?<=ID_" + fn_id + "\">).*?(?=<)", fn_i)[0]
                        text = re.sub("<span class=\"InsertNoteMarker\" id=\"InsertNoteID_" + fn_id + ".*?</span>", "<fn>" + fn_eintrag + "</fn>", text, re.DOTALL)
                        text = re.sub("<li id=\"InsertNoteID_" + fn_id + ".*?</li>", "", text)
                    
                    #fnx_list = re.findall("<a href=\"#InsertNoteIDX_(.*?)\">.*?</a>", text)
                    #text = text + fnx_list[0]
                    #for fnx in fnx_list:
                        #text = text + fnx
                        #fnx_tupel = re.split("\">", fnx)
                        #text = re.sub("<li id=\"InsertNoteIDX_" + fnx_tupel[0] + "\">", "<li>&8&" + fnx_tupel[1], text, re.DOTALL)
                    
                    #text = re.sub(r"<span id=\"InsertNoteIDX.*?</span>", "", text)

                    
                    # Ausgabe in ein Tag mit dem Feldnamen
                    #-----------------------------------------
                    string_text += '\n' + "<" + i + ">" + '\n'  
                    string_text += text                  
                    string_text += '\n' + "</" + i + ">" + '\n'

                
            except:
                pass

        ausgabe.close()

        # Ausgabe in die Datei 'ymir_zwischen.xml'   
        #-------------------------------------------------------------------    
        ausgabe = codecs.open(pfad + 'ymir_zwischen.xml', "w", "utf8") 
        ausgabe.write(string_text)
        ausgabe.close()


            
        
        string_text = "<bttitel>" + str(pstate.object_title()) + "</bttitel>\n" + "<titel>" + str(pstate.object_title()) + "</titel>\n"+ string_text
        string_text = "<dokument>\n" + string_text + "\n</dokument>"
        
        # Ausgabe in die Datei 'ymir.xml'   
        #-------------------------------------------------------------------    
        ausgabe = codecs.open(pfad + 'ymir.xml', "w", "utf8") 
        ausgabe.write(string_text)
        ausgabe.close()


        # Bearbeitung der Rohdaten
        #-------------------------------------------------------------------    
        baum = dom.parse(pfad + 'ymir.xml')

        ausgabe = codecs.open(pfad + 'ymir.xml', "w", "utf8") 
        ausgabe.write("geparsed")
        ausgabe.close()

        typ = baum.lastChild.getElementsByTagName("type")[0].firstChild.data 

        ausgabe = codecs.open(pfad + 'type.xml', "w", "utf8") 
        ausgabe.write(typ)
        ausgabe.close()

        felder = ["bttitel", "description", "text"]
        if typ == "Quellentext":
            felder = ["titel", "histort", "stddatum", "regest", "fundort", "druckort", "originaltext", "uebetragung", "erlauterung", "aboutauthors", "ersteller"]
        if typ == "Fachartikel":
            felder = ["bttitel", "untertitel", "ersteller", "fachartikeltext", "fabstract", "aboutauthors"]

        text = ""
        for i in felder:
            try:
                text += baum.lastChild.getElementsByTagName(i)[0].toxml() + "\n"
            except:
                pass

        text = re.sub("</bttitel>.*?\n.*?<untertitel>", "</bttitel><untertitel>", text, re.DOTALL) 
        ausgabe = codecs.open(pfad + 'ymir.xml', "w", "utf8") 
        ausgabe.write(text)
        ausgabe.close()    

        pstate = getMultiAdapter((self.context, self.request), name='plone_context_state')
        obj_title_pdf = eigenname + '.pdf'
            
        # Aufruf von Tustep / PDF-Erzeugung und Übergabe
        #-------------------------------------------------------------------
        os.system('tcsh -c "tustep 1"')
        os.system('ps2pdf ' + pfad + 'buri.ps ' + pfad + 'buri.pdf')
        shutil.copy (pfad + 'buri.pdf', '/var/www/tustep_pdf/' + obj_title_pdf)
        
        obj = pstate.object_title()
        self.objid = eigenname
        self.ergebnisse = obj
        self.ergebnisseurl = "http://germa61.uni-trier.de/tustep_pdf/" + obj_title_pdf
        return self.result_template()
                


"""
    @form.action('einstellungen')
    def actioneinstellungen(self, action, data):
        # Put the action handler code here 
        pstate = getMultiAdapter((self.context, self.request), name='plone_context_state')
        url = pstate.current_base_url()
        url = re.sub('/tustepform','',url)
        obj = pstate.object_title()
        self.ergebnisse = obj
        return self.result_template()
        #return ("http://germa61.uni-trier.de/tustep_pdf/buri.pdf")
"""





