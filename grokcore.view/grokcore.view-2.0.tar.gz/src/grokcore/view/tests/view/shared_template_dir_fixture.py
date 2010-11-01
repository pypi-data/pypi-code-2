"""
This should issue a UserWarning.
"""
import grokcore.view as grok
from shared_template_dir import Mammoth

grok.templatedir("shared_templates")

class Food(grok.View):
    grok.context(Mammoth)

