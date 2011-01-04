"""Definition of the Quellentext content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *

from types import StringType

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes import ATCTMessageFactory as _

from rc.docs import docsMessageFactory as _
from rc.docs.interfaces import IQuellentext
from rc.docs.config import PROJECTNAME

QuellentextSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

# QuellentextSchema = BaseSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    
    atapi.StringField(
        'title',
        required=True,
        searchable=True,
        default='',
        accessor='Title',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_("Überschrift"),
        ),
    ),
    
    atapi.StringField(
        'shorttitle',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Kurztitel"),
            description=_(u"Nachname des Bearbeiters, Erscheinungsjahr der Quelle und die ersten Zeichen des Titels."),
        ),
        required=False,
        #accessor='shorttitle',
    ),

    atapi.StringField(
        'kopfregest',
        required=False,
        searchable=True,
        default='',
#        accessor='kopfregest',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_("Kopfregest"),
            description=_(u"Beschreibung zum Kopfregest."),
        ),
    ),

    atapi.StringField(
        'seqnumber',
        required=False,
        searchable=True,
        default='',
#        accessor='seqnumber',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_("Laufende Nummer"),
            description = _(u"Beschreibung laufende Nummer.")
        ),
    ),
    
    atapi.StringField(
        'histdatum',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Historisches Entstehungsdatum"),
            description=_(u"Bitte das Datum eintragen falls bekannt."),
        ),
        required=False,
        searchable=1,
    ),  
    
    atapi.StringField(
        'stddatum',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Standardisiertes Datum"),
            description=_(u"Bitte das Datum eintragen falls bekannt."),
        ),
        required=False,
    ),
    
    atapi.StringField(
        'histort',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Historisches Entstehungsort"),
            description=_(u"Entstehungsort/Ort/Ausstellungsort."),
        ),
        required=False,
    ),    
    
    atapi.TextField(
        'fundort',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Fundort"),
            description=_(u"ID oder String."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
        required=False,
    ),
    
    atapi.TextField(
        'druckort',
        storage=atapi.AnnotationStorage(),
#        validators=('isURL',),
        widget=atapi.RichWidget(
            label=_(u"Druckort"),
            description=_(u"ID oder String."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
        required=False,
    ),

    atapi.TextField(
        'regest',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Regest"),
            description=_(u"Kurzbeschreibung eingeben."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),


    atapi.TextField(
        'originaltext',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"(Original-)text"),
            description=_(u"Text erfassen."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),
    
    atapi.TextField(
        'uebetragung',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_("Übertragung"),
            description=_(u"Text &uuml;bertragen."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),
        
    atapi.TextField(
        'erlauterung',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Interpretation"),
            description=_(u"Interpretation."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),
    
    atapi.TextField(
        'notiz',
        schemata="FuD-Notizen",
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Notizen"),
            description=_(u"Hier k&ouml;nnen Sie Ihre Notizen eintragen."),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=0,
    ),    
    
    atapi.TextField(
        'iedit',
        schemata="laufzettel",
        storage=atapi.AnnotationStorage(),
        default=r"""<table class="plain" style="width: 960px;"> <tr> <td width="120">
        <p><b>Menü</b></p> </td> <td width="200"> <p><b>Aufgaben</b></p> </td>
        <td width="200"> <p><b>Beschreibung/Hinweise</b></p> </td> <td width="110">
        <p><b>Autor</b></p> </td> <td width="110"> <p><b>Redakteur</b></p> </td>
        <td width="110"> <p><b>Lektor</b></p> </td> <td width="110">
        <p><b>Herausgeber</b></p> </td> </tr> <tr> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td> <p><b>Texterstellung</b></p> </td> <td>
        <p><b>redakt. Bearb.</b></p> </td> <td> <p><b>Lektorat</b></p> </td>
        <td> <p><b>Publ.-Vorb.</b></p> </td> </tr> <tr> <td> <p><b>Kopfregest</b>
        </p> </td> <td> <p>(Ausstellungs-)Datum normalisieren</p> </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        </tr> <tr> <td>&#160; </td> <td> <p>(Ausstellungs-)Ort prüfen/nachtragen</p>
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td> <p>Archivabkürzungen
        prüfen und gffs. normalisieren</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <td>&#160;
        </td> <td> <p>Kopfregest prüfen/umformulieren</p> </td> <td>&#160; </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr>
        <tr> <td>&#160; </td> <td> <p>Fundort: Archivangaben normalisieren/prüfen</p>
        </td> <td><p>Kurztitel (Link) aus der Bibliographie eintragen</p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        </tr> <tr> <td>&#160; </td> <td> <p>Fundort: weitere Fundorte
        nachtragen</p> </td> <td><p>dto</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td>
        <p>Druckort: Angaben prüfen, vervollständigen</p> </td> <td>&#160; </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr>
        <tr> <td>&#160; </td> <td> <p>Druckort: Stimmt der Kurztitel?</p> </td>
        <td><p>Kurztitel (Link) aus der Bibliographie eintragen</p> </td> <td>
        &#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr>
        <td>&#160; </td> <td> <p>Druckort: weitere Angaben nachtragen</p> </td>
        <td><p>dto</p> </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </tr> <tr> <td> <p><b>Regest</b></p> </td> <td> <p>
        Regest erstellen, ergänzen, umformulieren</p> </td> <td>&#160; </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        </tr> <tr> <td>&#160; </td> <td> <p>Regest prüfen, korrigieren</p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </tr> <tr> <td> <p><b>(Original-)Text</b></p> </td> <td>
        <p>Text erstellen, ergänzen,</p> </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr> <td>&#160;
        </td> <td> <p>Text prüfen, korrigieren</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr>
        <td>&#160; </td> <td> <p>ggf. Kodierung der Sonderzeichen prüfen</p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </tr> <tr> <td> <p><b>Übersetzung</b></p> </td> <td>
        <p>Übersetzung/Übertragung anfertigen</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr>
        <td>&#160; </td> <td> <p>Übersetzung prüfen/korrigieren</p> </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160;
        </td> </tr> <tr> <td> <p><b>Kommentar</b></p> </td> <td> <p>Kommentar
        entwerfen(FuD-Kommentar berücksichtigen)</p> </td> <td><p>Bearbeitungshinweise,
        die im Kommentar enthalten sind, bearbeiten bzw. prüfen, ob die
        Bearbeitung schon erfolgt ist.</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td>
        <p>Kommentar prüfen, korrigiern</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr> <td>
        <p><b>Texterläuterung</b></p> </td> <td> <p>Erläuterungstext entwerfen
        </p> </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td> <p>Erläuterungstext
        prüfen, korrigieren</p> </td> <td>&#160; </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> </tr> </table>""",
        widget=atapi.RichWidget(
            label=_(u"Inhaltliche Bearbeitung"),
            description=_(u"ToDos"),
            rows="25",
        ),
        default_output_type='text/x-html-safe',
        searchable=0,
    ),    

    atapi.TextField(
        'sedit',
        schemata="laufzettel",
        storage=atapi.AnnotationStorage(),
        default=r"""<table class="plain" style="width: 960px;"> <tr> <td width="120">
        <p><b>Menü</b></p> </td> <td width="200"> <p><b>Aufgaben</b></p> </td>
        <td width="200"> <p><b>Beschreibung/Hinweise</b></p> </td> <td width="110">
        <p><b>Autor</b></p> </td> <td width="110"> <p><b>Redakteur</b></p> </td>
        <td width="110"> <p><b>Lektor</b></p> </td> <td width="110"> <p><b>
        Herausgeber</b></p> </td> </tr> <tr> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> <td> <p><b>Texterstellung</b></p> </td> <td> <p>
        <b>redakt. Bearb.</b></p> </td> <td> <p><b>Lektorat</b></p> </td> <td>
        <p><b>Publ.-Vorb.</b></p> </td> </tr> <tr> <td>&#160; </td> <td>
        <p>orthographische Richtigkeit</p> </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> </tr> <tr>
        <td>&#160; </td> <td> <p>grammatikalische Richtigkeit</p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td> <p>stilistische
        Richtigkeit</p> </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> <td>&#160; </td> </table>""",
        widget=atapi.RichWidget(
            label=_(u"Sprachliche Bearbeitung"),
            description=_(u"ToDos"),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=0,
    ),    
    
    atapi.TextField(
        'fedit',
        schemata="laufzettel",
        storage=atapi.AnnotationStorage(),
        default=r"""<table class="plain" style="width: 960px;"> <tr> <td width="120">
        <p><b>Menü</b></p> </td> <td width="200"> <p><b>Aufgaben</b></p> </td>
        <td width="200"> <p><b>Beschreibung/Hinweise</b></p> </td> <td width="110">
        <p><b>Autor</b></p> </td> <td width="110"> <p><b>Redakteur</b></p> </td>
        <td width="110"> <p><b>Lektor</b></p> </td> <td width="110"> <p>
        <b>Herausgeber</b></p> </td> </tr> <tr> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> <td> <p><b>Texterstellung</b></p> </td> <td> <p><b>redakt.
        Bearb.</b></p> </td> <td> <p><b>Lektorat</b></p> </td> <td> <p><b>Publ.-
        Vorb.</b></p> </td> </tr> <tr> <td>&#160; </td> <td> <p>Literatureinträge
        prüfen (richtiger Kurztitel vollständig und richtig in der Datenbank erfasst)
        </p> </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160;
        </td> <td>&#160; </td> </tr> <tr> <td>&#160; </td> <td> <p>Formattypen der
        Textbestandteile prüfen (Überschriften, Textkorpus, Fussnoten) </p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160;
        </td> </tr> <tr> <td>&#160; </td> <td> <p>Bilder (Position markiert,
        Qualität geprüft, Druckvorlage geprüft, Untertitel vorhanden) </p> </td>
        <td>&#160; </td> <td>&#160; </td> <td>&#160; </td> <td>&#160; </td>
        <td>&#160; </td> </table>""",
        widget=atapi.RichWidget(
            label=_(u"Formale Bearbeitung"),
            description=_(u"ToDos"),
            rows=15,
        ),
        default_output_type='text/x-html-safe',
        searchable=0,
    ),  
    
    
    atapi.LinesField(
        'sub',
        multiValued=1,
#        accessor="getSub",
        searchable=True,
#        storage=atapi.AnnotationStorage(),
        languageIndependent=True,
        vocabulary=(),
        schemata="categorization",
        widget=atapi.KeywordWidget(
            label=_(u'Sachindex'),
            description=_(u'help_categories',
                          default=u'Also known as keywords, tags or labels, '
                          'these help you categorize your content.'),
        ),
    ),

        atapi.LinesField(
        'orte',
        multiValued=1,
        searchable=True,
        languageIndependent=True,
        vocabulary=(),
        schemata="categorization",
        widget=atapi.KeywordWidget(
            label=_(u'Ortsindex'),
            description=_(u'help_categories',
                          default=u'Also known as keywords, tags or labels, '
                          'these help you categorize your content.'),
        ),
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

QuellentextSchema['title'].storage = atapi.AnnotationStorage()
QuellentextSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(QuellentextSchema, moveDiscussion=False)

# Hide the 'description' field
QuellentextSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('ownership').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
QuellentextSchema.get('effectiveDate').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
QuellentextSchema.get('expirationDate').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('creation_date').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('modification_date').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('creators').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('contributors').widget.visible = {'view': 'invisible', 'edit': 'invisible', }
#QuellentextSchema.get('rights').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class Quellentext(base.ATCTContent):
    """Quellentext zum Projekt einfügen"""
    implements(IQuellentext)

    meta_type = "Quellentext"
    schema = QuellentextSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    shorttitle = atapi.ATFieldProperty('shorttitle')
    shorttitle = atapi.ATFieldProperty('kopfregest')
    shorttitle = atapi.ATFieldProperty('seqnumber')
    histdatum = atapi.ATFieldProperty('histdatum')
    stddatum = atapi.ATFieldProperty('stddatum')
    histort = atapi.ATFieldProperty('histort')
    fundort = atapi.ATFieldProperty('fundort')
    druckort = atapi.ATFieldProperty('druckort')
    regest = atapi.ATFieldProperty('regest')
    originaltext = atapi.ATFieldProperty('originaltext')
    uebertragung = atapi.ATFieldProperty('uebertragung')
    erlauterung = atapi.ATFieldProperty('erlauterung')
    notiz = atapi.ATFieldProperty('notiz')
    iedit = atapi.ATFieldProperty('iedit')
    sedit = atapi.ATFieldProperty('sedit')
    fedit = atapi.ATFieldProperty('fedit')
#    sub = atapi.ATFieldProperty('sub')

    
    security       = ClassSecurityInfo()

#    security.declareProtected(ChangeSubs, 'setSub')
    #def setSub(self, value, alreadySet=False, **kw):
        #if type(value) is StringType:
            #value = (value,)
        #elif not value:
            #value = ()
        #f = self.getField('sub')
        #f.set(self, value, **kw) # set is ok
        #if not alreadySet:
            #self.setSub(value, alreadySet=True, **kw)
            
    #def getSub(self):
        #f=self.getField('sub')
        #result = self.collectKeywords('sub', f.accessor)
        #return tuple(result)

atapi.registerType(Quellentext, PROJECTNAME)
