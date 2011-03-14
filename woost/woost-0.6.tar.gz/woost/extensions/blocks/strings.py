#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations

# BlocksPage
#------------------------------------------------------------------------------
translations.define("BlocksPage",
    ca = u"Pàgina de blocs",
    es = u"Página de bloques",
    en = u"Blocks page"
)

translations.define("BlocksPage-plural",
    ca = u"Pàgines de blocs",
    es = u"Páginas de bloques",
    en = u"Blocks pages"
)

translations.define("BlocksPage.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Block
#------------------------------------------------------------------------------
translations.define("Block",
    ca = u"Bloc",
    es = u"Bloque",
    en = u"Block"
)

translations.define("Block-plural",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define("Block.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Block.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Block.css_class",
    ca = u"Classes CSS",
    es = u"Clases CSS",
    en = u"CSS classes"
)

# ImageGalleryBlock
#------------------------------------------------------------------------------
translations.define("ImageGalleryBlock",
    ca = u"Galeria d'imatges",
    es = u"Galería de imágenes",
    en = u"Image gallery"
)

translations.define("ImageGalleryBlock.gallery_type",
    ca = u"Tipus de galeria",
    es = u"Tipo de galería",
    en = u"Gallery type"
)

translations.define("ImageGalleryBlock.gallery_type-thumbnails",
    ca = u"Miniatures",
    es = u"Miniaturas",
    en = u"Thumbnails"
)

translations.define("ImageGalleryBlock.gallery_type-slideshow",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slideshow"
)

translations.define("ImageGalleryBlock.images",
    ca = u"Imatges",
    es = u"Imágenes",
    en = u"Images"
)

translations.define("ImageGalleryBlock-plural",
    ca = u"Galeries",
    es = u"Galerías",
    en = u"Image galleries"
)

translations.define("ImageGalleryBlock.thumbnail_width",
    ca = u"Amplada de les miniatures",
    es = u"Ancho de las miniaturas",
    en = u"Thumbnail width"
)

translations.define("ImageGalleryBlock.thumbnail_height",
    ca = u"Alçada de les miniatures",
    es = u"Alto de las miniaturas",
    en = u"Thumbnail height"
)

translations.define("ImageGalleryBlock.full_width",
    ca = u"Amplada de les imatges ampliades",
    es = u"Ancho de las imágenes ampliadas",
    en = u"Zoom in image width"
)

translations.define("ImageGalleryBlock.full_height",
    ca = u"Alçada de les miniatures",
    es = u"Alto de las miniaturas",
    en = u"Zoom in image height"
)

# ContainerBlock
#------------------------------------------------------------------------------
translations.define("ContainerBlock",
    ca = u"Contenidor",
    es = u"Contenedor",
    en = u"Container"
)

translations.define("ContainerBlock-plural",
    ca = u"Contenidors",
    es = u"Contenedores",
    en = u"Containers"
)

translations.define("ContainerBlock.blocks",
    ca = u"Blocs fills",
    es = u"Bloques hijos",
    en = u"Child blocks"
)

# BannerBlock
#------------------------------------------------------------------------------
translations.define("BannerBlock",
    ca = u"Banner",
    es = u"Banner",
    en = u"Banner"
)

translations.define("BannerBlock-plural",
    ca = u"Banners",
    es = u"Banners",
    en = u"Banners"
)

translations.define("BannerBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("BannerBlock.text-explanation",
    ca = u"""En cas de no especificar-se s'utilitzarà el títol de l'element
destí""",
    es = u"""En caso de no especificarse se utilitzará el título del
elemento destino""",
    en = u"If not text is provided the title from the target item will be used"
)

translations.define("BannerBlock.target",
    ca = u"Destí",
    es = u"Destino",
    en = u"Target"
)

translations.define("BannerBlock.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

# MenuBlock
#------------------------------------------------------------------------------
translations.define("MenuBlock",
    ca = u"Menú",
    es = u"Menú",
    en = u"Menu"
)

translations.define("MenuBlock-plural",
    ca = u"Menús",
    es = u"Menús",
    en = u"Menus"
)

translations.define("MenuBlock.root",
    ca = u"Arrel",
    es = u"Raiz",
    en = u"Root"
)

translations.define("MenuBlock.root_visible",
    ca = u"Arrel visible",
    es = u"Raiz visible",
    en = u"Root visible"
)

translations.define("MenuBlock.max_depth",
    ca = u"Profunditat màxima",
    es = u"Profundidad máxima",
    en = u"Maximum depth"
)

translations.define("MenuBlock.expanded",
    ca = u"Expandit",
    es = u"Expandido",
    en = u"Expanded"
)

# RichTextBlock
#------------------------------------------------------------------------------
translations.define("RichTextBlock",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("RichTextBlock-plural",
    ca = u"Textos",
    es = u"Textos",
    en = u"Texts"
)

translations.define("RichTextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("RichTextBlock.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

# TranslatedRichTextBlock
#------------------------------------------------------------------------------
translations.define("TranslatedRichTextBlock",
    ca = u"Text traduïble",
    es = u"Texto traducible",
    en = u"Translated text"
)

translations.define("TranslatedRichTextBlock-plural",
    ca = u"Textos traduïbles",
    es = u"Textos traducibles",
    en = u"Translated texts"
)

translations.define("TranslatedRichTextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("TranslatedRichTextBlock.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

# VimeoBlock
#------------------------------------------------------------------------------
translations.define("VimeoBlock",
    ca = u"Vídeo de Vimeo",
    es = u"Video de Vimeo",
    en = u"Vimeo video"
)

translations.define("VimeoBlock-plural",
    ca = u"Vídeos de Vimeo",
    es = u"Vídeos de Vimeo",
    en = u"Vimeo videos"
)

translations.define("VimeoBlock.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("VimeoBlock.video_width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("VimeoBlock.video_width-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

translations.define("VimeoBlock.video_height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("VimeoBlock.video_height-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

