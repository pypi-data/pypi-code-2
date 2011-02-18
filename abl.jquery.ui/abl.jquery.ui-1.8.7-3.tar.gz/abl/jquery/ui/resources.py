# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os
from functools import partial
import pkg_resources
import logging

from tw.api import JSLink, CSSLink
from abl.jquery.core.base import collect_variants
from abl.jquery.core import jquery_js

logger = logging.getLogger(__name__)

modname = __name__
basedir = "static/javascript/ui"

collect_variants = partial(collect_variants, basedir, modname=modname)


def register_theme(theme_name, modname, basedir):
    global THEMES, CSS_NAMES
    basedir = basedir.rstrip("/")
    res = {}
    for name in CSS_NAMES:
        filename = "/".join([basedir, "jquery.ui.%s.css" % name])
        if not pkg_resources.resource_exists(modname, filename):
            # try it again with the old style named themes
            filename = "/".join([basedir, "ui.%s.css" % name])
            if not pkg_resources.resource_exists(modname, filename):
                logger.error("File %s/%s for theme %s doesn't exist!", modname, basedir, theme_name)
        res[name] = CSSLink(filename=filename, modname=modname)
    THEMES[theme_name] = res


CSS_NAMES = ["base", "accordion", "core", "datepicker", "dialog", "progressbar", "resizable",
             "slider", "tabs", "theme", "autocomplete"]

THEMES = {}


for theme in ("base", "smoothness"):
    register_theme(theme, modname, "static/css/ui/themes/%s" % theme)


class ThemedCSSLink(CSSLink):
    """
    A CSS-link that looks up it's actual link through the `THEMES`-dictionary,
    based on the current setting of abl.jquery.ui.DEFAULT_THEME
    """

    params = dict(name="The name of the css-file out of CSS_NAMES")

    name = None

    def __init__(self, *args, **kwargs):
        name = kwargs["name"]
        arges = ("jquery_ui_themed_css_link_%s" % name,) + args
        super(ThemedCSSLink, self).__init__(*args, **kwargs)


    def update_params(self, d):
        super(ThemedCSSLink, self).update_params(d)

        d.link = self._css.link


    def __hash__(self):
        return hash(self.name)


    def __eq__(self, other):
        if not isinstance(other, ThemedCSSLink):
            return False
        return self.name == other.name


    def active_filename(self):
        # this is needed so that
        # aggregation works.
        return self._css.active_filename()


    @property
    def _css(self):
        assert self.name is not None
        import abl.jquery.ui as ui
        theme = THEMES[ui.DEFAULT_THEME]
        css = theme[self.name]
        return css


    @property
    def modname(self):
        return self._css.modname

ui_theme_css = ThemedCSSLink(name="theme")
ui_base_css = ThemedCSSLink(name="base")
ui_core_css = ThemedCSSLink(name="core")
ui_dialog_css = ThemedCSSLink(name="dialog")
ui_tabs_css = ThemedCSSLink(name="tabs")
ui_slider_css = ThemedCSSLink(name="slider")
ui_progressbar_css = ThemedCSSLink(name="progressbar")
ui_resizable_css = ThemedCSSLink(name="resizable")
ui_accordion_css = ThemedCSSLink(name="accordion")
ui_autocomplete_css = ThemedCSSLink(name="autocomplete")
ui_datepicker_css = ThemedCSSLink(name="datepicker")




ui_core_js = JSLink(filename=collect_variants('jquery.ui.core.js'),
                    javascript=[jquery_js],
                    css=[ui_theme_css, ui_base_css, ui_core_css],
                    modname=modname)


ui_accordion_js = JSLink(filename=collect_variants('jquery.ui.accordion.js'), javascript=[ui_core_js], modname=modname,
                         css=[ui_accordion_css])

ui_datepicker_js = JSLink(filename=collect_variants('jquery.ui.datepicker.js'), javascript=[ui_core_js],
                              modname=modname, css=[ui_datepicker_css])

ui_widget_js = JSLink(filename=collect_variants('jquery.ui.widget.js'), javascript=[ui_core_js], css=[ui_dialog_css], modname=modname)
ui_position_js = JSLink(filename=collect_variants('jquery.ui.position.js'), javascript=[ui_core_js], css=[ui_dialog_css], modname=modname)
ui_button_js = JSLink(filename=collect_variants('jquery.ui.button.js'),
                      javascript=[ui_core_js,
                                  ui_widget_js],
                      css=[ui_dialog_css],
                      modname=modname)
ui_mouse_js = JSLink(filename=collect_variants('jquery.ui.mouse.js'),
                     javascript=[ui_core_js,
                                 ui_widget_js],
                     css=[ui_dialog_css],
                     modname=modname)
ui_draggable_js = JSLink(filename=collect_variants('jquery.ui.draggable.js'),
                         javascript=[ui_core_js,
                                     ui_mouse_js],
                         modname=modname)

ui_resizable_js = JSLink(filename=collect_variants('jquery.ui.resizable.js'),
                         javascript=[ui_core_js,
                                     ui_mouse_js],
                         modname=modname, css=[ui_resizable_css])
ui_dialog_js = JSLink(filename=collect_variants('jquery.ui.dialog.js'),
                      javascript=[ui_core_js,
                                  ui_button_js,
                                  ui_draggable_js,
                                  ui_position_js,
                                  ui_resizable_js],
                      css=[ui_dialog_css],
                      modname=modname)

ui_autocomplete_js = JSLink(filename=collect_variants('jquery.ui.autocomplete.js'),
                         javascript=[ui_core_js,
                                     ui_widget_js,
                                     ui_position_js],
                         css=[ui_autocomplete_css],
                         modname=modname)

ui_autocomplete_callbacks_js = JSLink(filename='static/javascript/ui.autocomplete.callbacks.js',
                                      javascript=[ui_autocomplete_js],
                                      modname=modname)

ui_droppable_js = JSLink(filename=collect_variants('jquery.ui.droppable.js'), javascript=[ui_core_js], modname=modname)
ui_progressbar_js = JSLink(filename=collect_variants('jquery.ui.progressbar.js'), javascript=[ui_core_js], modname=modname, css=[ui_progressbar_css])
ui_selectable_js = JSLink(filename=collect_variants('jquery.ui.selectable.js'), javascript=[ui_core_js], modname=modname)
ui_slider_js = JSLink(filename=collect_variants('jquery.ui.slider.js'), javascript=[ui_core_js, ui_mouse_js], modname=modname, css=[ui_slider_css])
ui_sortable_js = JSLink(filename=collect_variants('jquery.ui.sortable.js'), javascript=[ui_core_js], modname=modname)
ui_tabs_js = JSLink(filename=collect_variants('jquery.ui.tabs.js'), javascript=[ui_core_js], modname=modname, css=[ui_tabs_css])


##
## Effects
##

effects_core_js = JSLink(filename=collect_variants('jquery.effects.core.js'), javascript=[ui_core_js], modname=modname)
effects_blind_js = JSLink(filename=collect_variants('jquery.effects.blind.js'), javascript=[effects_core_js], modname=modname)
effects_bounce_js = JSLink(filename=collect_variants('jquery.effects.bounce.js'), javascript=[effects_core_js], modname=modname)
effects_clip_js = JSLink(filename=collect_variants('jquery.effects.clip.js'), javascript=[effects_core_js], modname=modname)
effects_drop_js = JSLink(filename=collect_variants('jquery.effects.drop.js'), javascript=[effects_core_js], modname=modname)
effects_explode_js = JSLink(filename=collect_variants('jquery.effects.explode.js'), javascript=[effects_core_js], modname=modname)
effects_fold_js = JSLink(filename=collect_variants('jquery.effects.fold.js'), javascript=[effects_core_js], modname=modname)
effects_highlight_js = JSLink(filename=collect_variants('jquery.effects.highlight.js'), javascript=[effects_core_js], modname=modname)
effects_pulsate_js = JSLink(filename=collect_variants('jquery.effects.pulsate.js'), javascript=[effects_core_js], modname=modname)
effects_scale_js = JSLink(filename=collect_variants('jquery.effects.scale.js'), javascript=[effects_core_js], modname=modname)
effects_shake_js = JSLink(filename=collect_variants('jquery.effects.shake.js'), javascript=[effects_core_js], modname=modname)
effects_slide_js = JSLink(filename=collect_variants('jquery.effects.slide.js'), javascript=[effects_core_js], modname=modname)
effects_transfer_js = JSLink(filename=collect_variants('jquery.effects.transfer.js'), javascript=[effects_core_js], modname=modname)

##
## i18n
##

ui_i18n_js = JSLink(filename=collect_variants('i18n/jquery-ui-i18n.js'), modname=modname)

ui_datepicker_ar_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ar.js'), modname=modname)
ui_datepicker_bg_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-bg.js'), modname=modname)
ui_datepicker_ca_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ca.js'), modname=modname)
ui_datepicker_cs_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-cs.js'), modname=modname)
ui_datepicker_da_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-da.js'), modname=modname)
ui_datepicker_de_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-de.js'), modname=modname)
ui_datepicker_es_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-es.js'), modname=modname)
ui_datepicker_fi_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-fi.js'), modname=modname)
ui_datepicker_fr_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-fr.js'), modname=modname)
ui_datepicker_he_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-he.js'), modname=modname)
ui_datepicker_hu_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-hu.js'), modname=modname)
ui_datepicker_hy_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-hy.js'), modname=modname)
ui_datepicker_id_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-id.js'), modname=modname)
ui_datepicker_is_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-is.js'), modname=modname)
ui_datepicker_it_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-it.js'), modname=modname)
ui_datepicker_ja_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ja.js'), modname=modname)
ui_datepicker_ko_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ko.js'), modname=modname)
ui_datepicker_lt_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-lt.js'), modname=modname)
ui_datepicker_lv_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-lv.js'), modname=modname)
ui_datepicker_nl_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-nl.js'), modname=modname)
ui_datepicker_no_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-no.js'), modname=modname)
ui_datepicker_pl_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-pl.js'), modname=modname)
ui_datepicker_pt_BR_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-pt-BR.js'), modname=modname)
ui_datepicker_ro_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ro.js'), modname=modname)
ui_datepicker_ru_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ru.js'), modname=modname)
ui_datepicker_sk_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sk.js'), modname=modname)
ui_datepicker_sv_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sv.js'), modname=modname)
ui_datepicker_th_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-th.js'), modname=modname)
ui_datepicker_tr_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-tr.js'), modname=modname)
ui_datepicker_uk_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-uk.js'), modname=modname)
ui_datepicker_zh_CN_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-zh-CN.js'), modname=modname)
ui_datepicker_zh_TW_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-zh-TW.js'), modname=modname)
ui_datepicker_el_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-el.js'), modname=modname)
ui_datepicker_sk_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sk.js'), modname=modname)
ui_datepicker_eo_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-eo.js'), modname=modname)
ui_datepicker_hr_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-hr.js'), modname=modname)
ui_datepicker_ms_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-ms.js'), modname=modname)
ui_datepicker_sl_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sl.js'), modname=modname)
ui_datepicker_sq_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sq.js'), modname=modname)
ui_datepicker_sr_SR_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sr-SR.js'), modname=modname)
ui_datepicker_sr_js = JSLink(javascript=[ui_datepicker_js], filename=collect_variants('i18n/jquery.ui.datepicker-sr.js'), modname=modname)
