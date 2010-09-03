from bn import AttributeDict
import logging

log = logging.getLogger('dreamweavertemplate')

def render_template(
    template=None, 
    template_from_config=None, 
    template_marble_name='template', 
    region_name='region',
    defaults=None,
):
    if template_from_config is None and template is None:
        raise Exception(
            "Expected either a 'template' or 'template_from_config' argument"
        )
    elif template_from_config is not None and template is not None:
        raise Exception(
            "Either the 'template' or 'template_from_config' argument "
            "should be specified, not both"
        )
    def outer(func):
        def inner(self, marble, *k, **p):
            bag = marble.bag
            if template_from_config is not None:
                template_ = bag.app.config[template_from_config]
            else:
                template_ = template
            region = AttributeDict()
            if defaults:
                region.update(defaults)
            if not bag.has_key(template_marble_name):
                bag.start(template_marble_name)
            p[region_name] = region
            result = func(self, marble, *k, **p)
            if result is not None:
                log.info(
                    'Not returning a rendered template because a result was '
                    'returned'
                )
                return result
            return bag[template_marble_name].render(
                template_,
                region,
            )
        return inner
    return outer


