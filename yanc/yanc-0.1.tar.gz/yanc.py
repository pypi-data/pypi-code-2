import re

from nose.plugins import Plugin

import termstyle


class ColorStreamProxy(object):
    
    _colors = {
        "OK" : ["green", "ok", "."],
        "ERROR" : ["red", "FAILED", "errors", "E"],
        "FAILURE" : ["yellow", "F"],
        "SKIP" : ["magenta", "S"],
        "-" * 70 : ["blue", "=" * 70],
        "testname" : ["cyan"],
        }
    
    def __init__(self, stream):
        self._stream = stream
        self._color_map = {}
        self._patten_map = {}
        for key, labels in self._colors.items():
            color = labels.pop(0)
            labels.append(key)
            for label in labels:
                self._color_map[label] = color
                if len(label) > 1:
                    self._patten_map[label] = re.compile("%s=\d+" % label)
        
    def __getattr__(self, key):
        return getattr(self._stream, key)
    
    def _colorize(self, string, color=None):
        if string:
            if color is None:
                color = self._color_map.get(string)
                if color is None:
                    for key in self._color_map:
                        if string.startswith(key + ":"):
                            # this is a test failure
                            segments = string.split(":")
                            return self._colorize(segments[0] + ":",
                                                  self._color_map[key]) \
                                + self._colorize(":".join(segments[1:]),
                                                 self._color_map["testname"])
                    for key, key_color in self._color_map.items():
                        pattern = self._patten_map.get(key)
                        if pattern is not None:
                            for match in pattern.findall(string):
                                string = string.replace(match, self._colorize(match, key_color))
            if color is not None:
                string = termstyle.bold(getattr(termstyle, color)(string))
            return string
    
    def write(self, string):
        self._stream.write(self._colorize(string))
    
    def writeln(self, string=""):
        self._stream.writeln(self._colorize(string))

    
class YANC(Plugin):
    """Yet another nose colorer"""
    
    name = "yanc"
    
    _options = (
        ("color", "YANC color override - one of on,off [%s]", "store"),
        )
    
    def options(self, parser, env):
        super(YANC, self).options(parser, env)
        for name, help, action in self._options:
            env_opt = "NOSE_YANC_%s" % name.upper()
            parser.add_option("--yanc-%s" % name.replace("_", "-"),
                              action=action,
                              dest="yanc_%s" % name,
                              default=env.get(env_opt),
                              help=help % env_opt)
        
    
    def configure(self, options, conf):
        super(YANC, self).configure(options, conf)
        for name, help, dummy in self._options:
            name = "yanc_%s" % name
            setattr(self, name, getattr(options, name))
        self.color = self.yanc_color !="off" \
                         and (self.yanc_color == "on" \
                             or (hasattr(self.conf.stream, "isatty") \
                                 and self.conf.stream.isatty()))
        
    def begin(self):
        if self.color:
            self.conf.stream = ColorStreamProxy(self.conf.stream)
    
    def finalize(self, result):
        if self.color:
            self.conf.stream = self.conf.stream._stream
    