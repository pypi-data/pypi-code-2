from gae import template
from gae import webapp
from gae.tags import node_rule, BaseNode
import logging

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("[adv_name]",))
def show_banner(self, context):
    '''Show specified banner'''
    try:
        return webapp.instance.render("banner/%s" % self.adv_name)
    except Exception:
        logging.warning("Banner '%s' not found", self.adv_name)
        return ''