from Products.Archetypes.public import *
from Products.Archetypes import atapi
from Products.ATContentTypes.interface import IATFolder
from Products.ATContentTypes.interface import IATDocument
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implements

class ShortTitleField(ExtensionField, StringField): pass
class ArticleTypeField(ExtensionField, StringField): pass
class ArticleLanguage(ExtensionField, StringField): pass
class OriginalArticleLanguage(ExtensionField, StringField): pass
class AvailableLanguages(ExtensionField, LinesField): pass
class Editor(ExtensionField, StringField): pass
class Publisher(ExtensionField, StringField): pass
class Translator(ExtensionField, StringField): pass
class TimeFrom(ExtensionField, IntegerField): pass
class TimeUntil(ExtensionField, IntegerField): pass
class Area(ExtensionField, LinesField): pass
class Topic(ExtensionField, LinesField): pass
class Licence(ExtensionField, StringField): pass
class UniqueCode(ExtensionField, StringField): pass
class URN(ExtensionField, StringField): pass
class DDC(ExtensionField, LinesField): pass
class PublicationDate(ExtensionField, DateTimeField): pass
class PreviewImage(ExtensionField, ImageField): pass
class MediaContentTypeField(ExtensionField, StringField): pass
class IsTranslation(ExtensionField, BooleanField): pass


class DocumentExtender(object):
    adapts(IATDocument)
    implements(ISchemaExtender)
    # ISO 639 2-letter codes
    # http://www.w3.org/WAI/ER/IG/ert/iso639.htm
    languages=[("DE","German"),
				("EN","English"),
				("FR","French"),
				("0","--------"),
    			("AB","Abkhazian"),
				("AA","Afar"),
				("AF","Afrikaans"),
				("SQ","Albanian"),
				("AM","Amharic"),
				("AR","Arabic"),
				("HY","Armenian"),
				("AS","Assamese"),
				("AY","Aymara"),
				("AZ","Azerbaijani"),
				("BA","Bashkir"),
				("EU","Basque"),
				("BN","Bengali"),
				("DZ","Bhutani"),
				("BH","Bihari"),
				("BI","Bislama"),
				("BR","Breton"),
				("BG","Bulgarian"),
				("MY","Burmese"),
				("BE","Byelorussian"),
				("KM","Cambodian"),
				("CA","Catalan"),
				("ZH","Chinese"),
				("CO","Corsican"),
				("HR","Croatian"),
				("CS","Czech"),
				("DA","Danish"),
				("NL","Dutch"),
				("EO","Esperanto"),
				("ET","Estonian"),
				("FO","Faeroese"),
				("FJ","Fiji"),
				("FI","Finnish"),
				("FR","French"),
				("FY","Frisian"),
				("GD","Gaelic"),
				("GL","Galician"),
				("KA","Georgian"),
				("EL","Greek"),
				("KL","Greenlandic"),
				("GN","Guarani"),
				("GU","Gujarati"),
				("HA","Hausa"),
				("IW","Hebrew"),
				("HI","Hindi"),
				("HU","Hungarian"),
				("IS","Icelandic"),
				("IN","Indonesian"),
				("IA","Interlingua"),
				("IE","Interlingue"),
				("IK","Inupiak"),
				("GA","Irish"),
				("IT","Italian"),
				("JA","Japanese"),
				("JW","Javanese"),
				("KN","Kannada"),
				("KS","Kashmiri"),
				("KK","Kazakh"),
				("RW","Kinyarwanda"),
				("KY","Kirghiz"),
				("RN","Kirundi"),
				("KO","Korean"),
				("KU","Kurdish"),
				("LO","Laothian"),
				("LA","Latin"),
				("LV","Latvian"),
				("LN","Lingala"),
				("LT","Lithuanian"),
				("MK","Macedonian"),
				("MG","Malagasy"),
				("MS","Malay"),
				("ML","Malayalam"),
				("MT","Maltese"),
				("MI","Maori"),
				("MR","Marathi"),
				("MO","Moldavian"),
				("MN","Mongolian"),
				("NA","Nauru"),
				("NE","Nepali"),
				("NO","Norwegian"),
				("OC","Occitan"),
				("OR","Oriya"),
				("OM","Oromo"),
				("PS","Pashto"),
				("FA","Persian"),
				("PL","Polish"),
				("PT","Portuguese"),
				("PA","Punjabi"),
				("QU","Quechua"),
				("RM","Rhaeto-Romance"),
				("RO","Romanian"),
				("RU","Russian"),
				("SM","Samoan"),
				("SG","Sangro"),
				("SA","Sanskrit"),
				("SR","Serbian"),
				("SH","Serbo-Croatian"),
				("ST","Sesotho"),
				("TN","Setswana"),
				("SN","Shona"),
				("SD","Sindhi"),
				("SI","Singhalese"),
				("SS","Siswati"),
				("SK","Slovak"),
				("SL","Slovenian"),
				("SO","Somali"),
				("ES","Spanish"),
				("SU","Sudanese"),
				("SW","Swahili"),
				("SV","Swedish"),
				("TL","Tagalog"),
				("TG","Tajik"),
				("TA","Tamil"),
				("TT","Tatar"),
				("TE","Tegulu"),
				("TH","Thai"),
				("BO","Tibetan"),
				("TI","Tigrinya"),
				("TO","Tonga"),
				("TS","Tsonga"),
				("TR","Turkish"),
				("TK","Turkmen"),
				("TW","Twi"),
				("UK","Ukrainian"),
				("UR","Urdu"),
				("UZ","Uzbek"),
				("VI","Vietnamese"),
				("VO","Volapuk"),
				("CY","Welsh"),
				("WO","Wolof"),
				("XH","Xhosa"),
				("JI","Yiddish"),
				("YO","Yoruba"),
				("ZU","Zulu"),]

    fields = [
        ShortTitleField(
            "shorttitle",
                widget = StringWidget(
                label=u"Short Title",
                il8n_domain='plone',
            ),
            required=False,
			searchable=True
        ),
        ArticleTypeField(
            "articletype",
            widget = SelectionWidget(
                label=u"Article Type",
                il8n_domain='plone',
            ),
            vocabulary=[("g","General"), ("mb", "Media Description"), ("t", "Thread"), ("be", "Basic Element"), ("ub","Overview"), ("ve", "In Depth Element")],
			required=False,
			searchable=True
        ),
        MediaContentTypeField(
            "mediacontent",
            widget = SelectionWidget(
                label=u"Media Content Type",
                description=u"If this is a Media Description please select the primary type of Content",
                il8n_domain='plone',
            ),
            vocabulary=[("n","No Media Description"),("a","Audio"), ("i", "Image"), ("v", "Video"), ("o", "Other")],
			required=False,
			searchable=True
        ),
        PreviewImage(
            "previewimage",
            widget = ImageWidget(
                label=u"Preview Image",
                description=u"This image is used as preview for search result pages",
            ),
			required=False,
			searchable=True
        ),
        ArticleLanguage(
			'articlelanguage',
			widget=atapi.SelectionWidget(
				label=u'Language',
				description=u"Which language is this article written in?",
			),
			vocabulary=languages,                                           
			required=False,
			searchable=True
		),
		IsTranslation(
			'istranslation',
			widget=atapi.BooleanWidget(
				label=u'This article is a translation from another language',
			),                                      
			required=False,
			searchable=True
		),
		OriginalArticleLanguage(
			'originallanguage',
			widget=atapi.SelectionWidget(
				label=u'Language of Original',
				description=u"Which language was this document translated from? If this is the original please select the same as above.",
			),
			vocabulary=languages, 
			required=False,
			searchable=True
		),
		AvailableLanguages(
			'availablelanguage',
			widget=atapi.PicklistWidget(
				label=u'Available Language',
				description=u"A list of all languages in which translations of this article are available",
				il8n_domain='pagetest',
			),
			vocabulary=languages, 
			required=False,
			searchable=True
		),
		Editor(
			'copyeditor',
			# Redaktion
			widget=atapi.StringWidget(
				label=u'Copy Editor',
				il8n_domain='plone',
			),
			required=False,
			searchable=True
		),
		Publisher(
			'publisher',
			# herausgeber
			widget=atapi.StringWidget(
				label=u'Publisher',
				il8n_domain='plone',
			),
			required=False,
			searchable=True
		),
		Translator(
			name='translator',
			widget=atapi.StringWidget(
				label=u'Translator',
				label_msgid='pagetest_label_translator',
				il8n_domain='pagetest',
			),
			required=False,
			searchable=True
		),
		TimeFrom(
			name='timefrom',
			widget=atapi.IntegerWidget(
				label=u'Time interval from (year)',
				description=u"This determines the time interval that is used for advanced search queries",
				size=4,
				maxlength=4,
			),
			required=False,
			searchable=True
		),
		TimeUntil(
			name='timeuntil',
			widget=atapi.IntegerWidget(
				label=u'until (year)',
				size=4,
				maxlength=4,
			),
			required=False,
			searchable=True
		),
		Area(
			name='area',
			widget=atapi.PicklistWidget(
				label=u'Area',
			),
			vocabulary_factory = "eg.theme.vocabularies.area",
			required=False,
			searchable=True
		),
		Topic(
			name='topic',
			widget=atapi.PicklistWidget(
				label=u'Topic',
			),
                        vocabulary_factory = "eg.theme.vocabularies.topics",
#			vocabulary=[("0","Education, Sciences"),
#		                ("1", "Arts"),
#		                ("2", "Social Matters, Society"),
#		                ("3", "Politics"),
#		                ("4", "Law, Constitution"),
#		                ("5", "Religion"),
#		                ("11", "Military"),
#		                ("6", "Migration, Travel"),
#		                ("7", "Media, Communication"),
#		                ("8", "Agents, Intermediaries"),
#		                ("9", "Theory, Methodology"),
#						("10", "Economy, Technology")],
			required=False,
			searchable=True
		),
		Licence(
			name='licence',
			widget=atapi.SelectionWidget(
				label=u'Licence',
			),
			vocabulary=[("cr", "All rights reserved"), ("by-nc-nd", "by-nc-nd - Attribution, Noncommercial, No Derivative Works")],
			required=False,
			searchable=True
		),
		UniqueCode(
			name='unique',
			widget=atapi.StringWidget(
				label=u'Short URL without language code',
				description=u'e.g. If the URL is http://www.ieg-ego.eu/boeschf-2010-de please enter boeschf-2010 here',
				il8n_domain='plone',
			),
			required=False,
			searchable=True
		),
		URN(
			name='urn',
			widget=atapi.StringWidget(
				label=u'URN',
				description=u'URN without resolver. e.g. urn:nbn:de:0159-20100921115',
				il8n_domain='plone',
			),
			required=False,
			searchable=True
		),
		DDC(
			name='DDC',
			widget=atapi.LinesWidget(
				label=u'DDC',
				description=u'Enter the relevant DDC codes, one per line.',
				il8n_domain='plone',
				cols=10,
			),
			required=False,
			searchable=True
		),
		PublicationDate(
			name='publicationsdate',
			widget=atapi.CalendarWidget(
				label=u'Publication date',
				description=u'Select the date that should appear as publication date in the page header',
				il8n_domain='plone',
				show_hm=False,
			),
			required=False,
			searchable=True
		),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
