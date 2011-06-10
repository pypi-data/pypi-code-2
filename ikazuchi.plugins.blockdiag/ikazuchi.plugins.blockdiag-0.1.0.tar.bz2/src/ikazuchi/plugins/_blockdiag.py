# -*- coding: utf-8 -*-

import codecs
import webbrowser
from os.path import getsize
from tempfile import NamedTemporaryFile
from time import sleep

# Tkinter
import Tkinter as Tk
import Image
import ImageTk
from ScrolledText import ScrolledText

from ikazuchi.core.translator import BaseTranslator
from ikazuchi.core.handler import BaseHandler
from ikazuchi.ikazuchi import (base_parser, subparsers)

__version__ = "0.1.0"

# argument parser for speech
diag_parser = subparsers.add_parser("blockdiag", parents=[base_parser])
diag_parser.set_defaults(diag_file=None, interactive=False, sentences=[])
diag_parser.add_argument("-d", "--diag", dest="diag_file",
    metavar="DIAG FILE", help=u"target diag file")
diag_parser.add_argument("-i", "--interactive", dest="interactive",
    action="store_true", help=u"run with interactive mode")
diag_parser.add_argument("-s", "--sentence", dest="sentence",
    metavar="SENTENCE", help=u"target sentence")
diag_parser.add_argument("--version", action="version",
    version="%(prog)s {0}".format(__version__))


class Translator(BaseTranslator):
    """
    Translator class for blockdiag
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler

    def translate(self, source, file_name, fmt):
        generate_blockdiag_image(source, file_name, fmt)

    def set_apikey_from_conf(self, conf):
        """No need to implement since blockdiag don't require api key"""


class Handler(BaseHandler):
    """
    Handler class for blockdiag
    """
    def __init__(self, opts):
        self.encoding = opts.encoding
        self.interactive = opts.interactive
        self.source = self._get_source(opts.sentence, opts.diag_file)
        self.image_format = "PNG" if self.interactive else "SVG"

    def _get_source(self, sentence, diag_file):
        source = u""
        if diag_file:
            with codecs.open(diag_file, "r", self.encoding[0]) as f:
                source = f.read()
        elif sentence:
            source = unicode(sentence, self.encoding[0])
        return source

    def _make_image_file(self, file_name):
        if getsize(file_name) == 0:
            image = Image.new("RGB", (1, 1), (256, 256, 256))
            image.save(file_name, "PNG")

    def _call_method(self, api_method):
        with NamedTemporaryFile(mode="wb") as tmp:
            api_method(self.source, tmp.name, self.image_format)
            if self.interactive:
                self._make_image_file(tmp.name)
                app = BlockdiagEditor(api_method, self.source, tmp.name)
                app.root.mainloop()
            else:
                self.show_diag_with_browser(tmp.name)

    def show_diag_with_browser(self, file_name):
        webbrowser.open_new_tab(file_name)
        sleep(1)


# user interface with Tkinter
_DIAG_LINK_PREFIX = "http://interactive.blockdiag.com/?src="

class BlockdiagEditor(object):
    """
    Interactive editor UI for blockdiag
    """
    def __init__(self, diag_method, source, diag_image):
        self.diag_method = diag_method
        self.source = intern(source.encode("utf-8"))
        self.image_format = "PNG"
        self.tmp = NamedTemporaryFile(mode="wb")
        self.root = Tk.Tk()
        self.root.geometry("1024x768")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Frames
        self.frame = Tk.Frame(self.root)
        self.frame.master.title("blockdiag editor")
        self.frame.pack(fill=Tk.BOTH, expand=1, padx=3, pady=3)
        self.btn_frame = Tk.Frame(self.frame)
        self.btn_frame.pack(fill=Tk.BOTH, padx=3, pady=3)
        self.text_frame = Tk.Frame(self.frame)
        self.text_frame.pack(fill=Tk.BOTH, expand=1, padx=3, pady=3)
        self.image_frame = Tk.Frame(self.frame)
        self.image_frame.pack(fill=Tk.BOTH, expand=1, padx=3, pady=3)
        self.image_frame.grid_rowconfigure(0, weight=1, minsize=0)
        self.image_frame.grid_columnconfigure(0, weight=1, minsize=0)

        # Button
        self.upd_btn = Tk.Button(self.btn_frame, bd=2, text="Update Canvas",
                                 command=self.redraw_diag_image)
        self.upd_btn.pack(side=Tk.LEFT)
        self.link_btn = Tk.Button(self.btn_frame, bd=2, text="Permanent link",
                                  command=self.open_permanent_link)
        self.link_btn.pack(side=Tk.LEFT)
        self.quit_btn = Tk.Button(self.btn_frame, bd=2, text="Quit",
                                  command=self.quit)
        self.quit_btn.pack(side=Tk.LEFT)

        # Text Editor
        self.text = ScrolledText(self.text_frame, wrap=Tk.WORD)
        self.text.pack(fill=Tk.BOTH, expand=1)
        self.text.insert(Tk.END, source)
        self.text.focus_set()
        self.text.bind("<KeyRelease-Control_L>", self.redraw_diag_image)
        self.text.bind("<KeyRelease-Control_R>", self.redraw_diag_image)

        # Image Viewer
        self.image = ImageTk.PhotoImage(file=diag_image)
        self.canvas = Tk.Canvas(self.image_frame, scrollregion=(0, 0,
                            self.image.width(), self.image.height()))
        self.canvas.grid(row=0, column=0, sticky=Tk.N + Tk.E + Tk.W + Tk.S)
        # Add Scrollbar
        xscr = Tk.Scrollbar(self.image_frame,
                orient=Tk.HORIZONTAL, command=self.canvas.xview)
        xscr.grid(row=1, column=0, sticky=Tk.E + Tk.W)
        yscr = Tk.Scrollbar(self.image_frame,
                orient=Tk.VERTICAL, command=self.canvas.yview)
        yscr.grid(row=0, column=1, sticky=(Tk.N, Tk.S))
        self.canvas.config(xscrollcommand=xscr.set, yscrollcommand=yscr.set)
        self.canvas.create_image(0, 0, image=self.image, anchor=Tk.NW)

    def redraw_canvas(self, file_name):
        self.image = ImageTk.PhotoImage(file=file_name)
        self.canvas.config(scrollregion=(0, 0,
                            self.image.width(), self.image.height()))
        self.canvas.create_image(0, 0, image=self.image, anchor=Tk.NW)

    def redraw_diag_image(self, event=None):
        source = intern(self.text.get("1.0", Tk.END).encode("utf-8"))
        if source is not self.source:
            self.diag_method(source, self.tmp.name, self.image_format)
            if getsize(self.tmp.name) > 0:
                self.redraw_canvas(self.tmp.name)
            self.source = source

    def open_permanent_link(self):
        url = self.make_permanent_link()
        webbrowser.open_new_tab(url)

    def make_permanent_link(self):
        import base64
        source = intern(self.text.get("1.0", Tk.END).encode("utf-8"))
        url = _DIAG_LINK_PREFIX + base64.urlsafe_b64encode(source)
        print url
        return url

    def quit(self):
        self.tmp.close()
        self.root.destroy()


def generate_blockdiag_image(source, file_name, fmt):
    """ parse and generate image with blockdiag
    Inspired from https://bitbucket.org/tk0miya/gae_blockdiag
    Thank you tk0miya-san!
    """
    from blockdiag import diagparser, builder, DiagramDraw
    if not source:
        return
    try:
        tree = diagparser.parse(diagparser.tokenize(source))
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = DiagramDraw.DiagramDraw(fmt, diagram, filename=file_name)
        draw.draw()
        draw.save("")
    except Exception as err:
        print u"blockdiag generate image error: {0}".format(err)
