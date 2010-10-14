from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import ImageWidget


class RichImageWidget(ImageWidget):
    """ """
    _properties = ImageWidget._properties.copy()
    _properties.update(dict(
        display_threshold = 102400,
        preview_scale = 'preview',
        crops = {'frontpage_top'     : (0, 0, 661, 214),
                 'focus'             : (0, 0, 233,  84),
                 'subject_page'      : (0, 0, 485, 214),
                 'person'            : (0, 0, 130, 155),
                 'publication_cover' : (0, 0,  80, 120),
                 'small'             : (0, 0,  80,  80),
                 'page'              : (0, 0, 209, 159),
                 'page_2_columns'    : (0, 0, 458, 159),
                 'content_wide'      : (0, 0, 482, 159),
                 'page_wide'         : (0, 0, 707, 159),
                 'category'          : (0, 0, 209, 159),
                 'gallery'           : (0, 0, 209, 209),},
        ))

registerWidget(
    RichImageWidget, title='Rich Image',
    description='Image with crop',
    used_for=('Products.ImageRepository.field.RichImageWidget',))
