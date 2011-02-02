import cssutils
import htmlcolor

from css_crawler.lib import log
import capture


class ColorExtractor:
    def __init__(self, log=log, stylesheets=[]):
        self._log = log
        self._stylesheets = stylesheets
        self._color_parser = htmlcolor.Parser()
        self.parsed_colors = {
                            'background-color': {},
                            'color': {},
                            'border-color': {}
                            }

    def extract_colors(self):
        for stylesheet in self._stylesheets:
            self._extract_colors(stylesheet)

    def _parse_color_and_update(self, color, key, selectors):
        try:
            self.parsed_colors[key].setdefault(
                '#%02x%02x%02x' % self._color_parser.parse(str(color)),
                []).extend([s.selectorText for s in selectors])
        except (ValueError, KeyError) as e:
            self._log.debug(
                'Value %s is not a valid css color: %r\n---\n%r',
                color, selectors, e)

    def _extract_colors(self, stylesheet):

        for rule in stylesheet.cssRules:

            if isinstance(rule, cssutils.css.CSSStyleRule):

                if 'background-color' in rule.style:
                    color = rule.style['background-color'].strip()
                    self._log.debug('found "background-color": %s', color)
                    self._parse_color_and_update(color, 'background-color',
                                                    rule.selectorList)

                if 'background' in rule.style:
                    #background can be one of the following:
                    # - background-color *
                    # - *
                    background = rule.style['background'].strip()
                    self._log.debug('found "background": %s', background)
                    if background != '':
                        color = background.split()[0]
                        self._parse_color_and_update(color, 'background-color',
                                                        rule.selectorList)

                if 'color' in rule.style:
                    color = rule.style['color'].strip()
                    self._log.debug('found "color": %s', color)
                    self._parse_color_and_update(color, 'color',
                                                    rule.selectorList)

                for border_property in ['border-color', 'border-top-color',
                        'border-bottom-color', 'border-left-color',
                        'border-right-color']:

                    if border_property in rule.style:
                        color = rule.style[border_property].strip()
                        self._log.debug('found "border-color": %s', color)
                        self._parse_color_and_update(color, 'border-color',
                                                        rule.selectorList)

                for border_property in ['border', 'border-top',
                    'border-bottom', 'border-left', 'border-right']:
                    #border can be one of the following:
                    # - border-width border-style border-color
                    # - border-width border-style
                    # - border-style
                    # - border-style border-color

                    if border_property in rule.style:
                        border = rule.style[border_property].strip()
                        self._log.debug('found "border": %s', border)
                        if border != '':
                            color = border.split()[-1]
                            self._parse_color_and_update(color,
                                'border-color', rule.selectorList)


def capture_and_extract_colors(url, log=log):
    ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) \
Gecko/20070515 Firefox/2.0.0.4'
    css_capture = capture.CSSCapture(ua, log)
    url, stylesheets = css_capture.capture(url)
    color_extractor = ColorExtractor(log, stylesheets)
    color_extractor.extract_colors()
    return url, color_extractor.parsed_colors
