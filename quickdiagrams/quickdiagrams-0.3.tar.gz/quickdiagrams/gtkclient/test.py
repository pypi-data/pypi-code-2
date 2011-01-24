# -*- encoding: utf-8-
# Copyright: Hugo Ruscitti <hugoruscitti@gmail.com>
# License: GPLv3

import os
import gtk
import re
import sys
import gtk.glade
import quickdiagrams
import dialogs
import gtkcodebuffer
import drawing_thread
import gobject
import pango
import lifoqueue


gobject.threads_init()

if sys.platform == "win32":
    TEMPORALY_FILEOUTPUT = "output.png"
else:
    TEMPORALY_FILEOUTPUT = "/tmp/output.png"


class View(object):
    pass


class Application:

    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(path, 'ui.glade')
        self.ui = gtk.glade.XML(file_path)
        self._connect_callbacks(self.ui)
        self._create_view(self.ui)
        self._create_buffer()

        self.queue = lifoqueue.LifoQueue()
        self.drawing_thread = drawing_thread.DrawingThread(self, self.queue)
        self.drawing_thread.start()

        self.buffer.connect("changed", self.custom_on_buffer__changed)

        background_color = gtk.gdk.color_parse("white")
        self.view.eventbox.modify_bg(gtk.STATE_NORMAL, background_color)
        self.request_draw_to_drawing_thread()
        self.last_lines_in_model = 0
        self.set_buffer_has_modified(False)
        self.document_name = ""
        self.view.statusimage.set_from_file('images/status_warning.png')
        self.view.statusimage.hide()
        self.last_filename_assigned = None

    def _create_buffer(self):
        emph  = gtkcodebuffer.String(r"\*", r"\*", style="datatype")
        emph2 = gtkcodebuffer.String(r"\*\*", r"\*\*", style="datatype")
        #code  = gtkcodebuffer.Pattern(r"asd", style="mark2")
        list1 = gtkcodebuffer.Pattern(r"^(- ).+$", style="comment", group=1)
        list2 = gtkcodebuffer.Pattern(r"^\s*-+", style="comment")
        head  = gtkcodebuffer.Pattern(r"^\s*[A-Z][a-z]*", style="keyword")
         
        lang = gtkcodebuffer.LanguageDefinition([emph, emph2, head, list1, list2])

        self.buffer = gtkcodebuffer.CodeBuffer(lang=lang)
        self.view.textview.set_buffer(self.buffer)

        pl = self.view.textview.create_pango_layout(' '*4)
        width, height = pl.get_pixel_size()

        ta = pango.TabArray(1, True)
        ta.set_tab(0, pango.TAB_LEFT, width)
        self.view.textview.set_tabs(ta)

        self.set_model_text("""Foro
	nombre
	mensajes
	----
	publicar
	
	ForoPrivado
		permisos
""")
        self.view.textview.grab_focus()

    def request_draw_to_drawing_thread(self):
        self.queue.put(self.draw_diagram)

    def custom_on_buffer__changed(self, widget):
        # Detecta si se ha creado una nueva linea.
        text_model = self.get_model_text_as_list()
        lines = len(text_model)

        if lines != self.last_lines_in_model:
            self.last_lines_in_model = lines

        self.request_draw_to_drawing_thread()

        self.set_buffer_has_modified(True)

    def update_status_indicator_line(self, w, iter, w3):
        line = iter.get_line()
        self.view.line.set_text("Cursor en la linea: %d" %(line))

    def set_buffer_has_modified(self, state):
        self.has_modified = state
        title = "quickdiagrams"

        if state:
            title = title + " [sin guardar]"
        
        self.view.save.set_sensitive(state)
        self.view.window.set_title(title)

    def draw_diagram(self):
        self.diagram = quickdiagrams.Diagram(disable_visible_warnings=True)
        text_model = self.get_model_text_as_list()
        self.diagram.read_from_string(text_model)
        errors = self.diagram.save(TEMPORALY_FILEOUTPUT, 'png', disable_output=True)
        self.update_image()
        self.update_message_bar(errors)
        self.buffer.connect("mark-set", self.update_status_indicator_line)

    def update_image(self):
        gobject.idle_add(self.update_image_callback)

    def update_image_callback(self):
        self.view.image.clear()
        self.view.image.set_from_file(TEMPORALY_FILEOUTPUT)

    def get_model_text_as_list(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end).split('\n')

    def update_message_bar(self, messages_to_show):
        
        if messages_to_show:
            self.view.statusbar.set_text(messages_to_show[0])
            self.view.statusimage.show()
        else:
            # Sin errores
            self.view.statusbar.set_text("")
            self.view.statusimage.hide()

    def set_model_text(self, text):
        self.buffer.set_text(text)

    def _connect_callbacks(self, ui):
        "Conecta automagicamente todos los eventos que parecen callbacks."

        expresion = re.compile("on_(.*)__(.*)")
        methods_list = [x for x in dir(self) if expresion.match(x)]

        for method in methods_list:
            result = expresion.search(method)
            widget_name = result.group(1)
            signal = result.group(2)

            widget = ui.get_widget(widget_name)
            function = getattr(self, method)
            widget.connect(signal, function)

    def _create_view(self, ui):
        "Extrae todas las referencias a widgets y las agrupa en 'view'."
        widgets_list = ui.get_widget_prefix("")
        self.view = View()

        for widget in widgets_list:
            name = widget.name
            setattr(self.view, name, widget)

    def save_to(self, filename):
        text_model_as_list = self.get_model_text_as_list()
        content = '\n'.join(text_model_as_list)
        file = open(filename, "wt")
        file.write(content)
        file.close()
        self.set_buffer_has_modified(False)
        self.last_filename_assigned = filename

    def open_file(self, filename):
        if filename.endswith('.py'):
            file = quickdiagrams.genqd.create_file_handler(filename)
        else:
            file = open(filename, "rt")

        self.set_model_text(file.read())
        file.close()
        self.set_buffer_has_modified(False)
        self.last_filename_assigned = filename

    def export_to(self, filename):
        self.diagram = quickdiagrams.Diagram()
        text_model = self.get_model_text_as_list()
        self.diagram.read_from_string(text_model)

        if sys.platform == "win32":
	    import shutil
            self.diagram.save("export.png", 'png')
	    shutil.copy("export.png", filename)


    # Callbacks
    def on_open__clicked(self, widget):
        pattern = ("ClassDiagram *.sc", "*.sc")
        pattern_py = ("Python files *.py", "*.py")
        dialog = dialogs.OpenDialog(self.view.window, pattern, self.open_file, pattern_py)
        dialog.run()

    def on_window__delete_event(self, widget, extra):
        "Intenta cerrar el programa pero consultando al usuario si no ha guardado."

        if not self.has_modified or self.show_confirm_dialog():
            gtk.main_quit()
            self.kill_child_thread()
        else:
            return True

    def kill_child_thread(self):
        "Intenta desbloquear el hilo que lee de la cola."
        self.queue.put(None)
        self.drawing_thread.join()

    def on_save__clicked(self, widget):
        pattern = ("ClassDiagram *.sc", "*.sc")
        dialog = dialogs.SaveDialog(self.view.window, pattern, self.save_to)
        dialog.run()

    def on_export__clicked(self, widget):
        pattern = ("PNG", "*.png")
        dialog = dialogs.SaveDialog(self.view.window, pattern, self.export_to)
        dialog.run()

    def on_about__clicked(self, widget):
        self.view.aboutdialog.run()
        self.view.aboutdialog.hide()

    def on_item_about__activate(self, widget):
        self.on_about__clicked(widget)

    def on_item_quit__activate(self, widget):
        self.on_window__delete_event(widget, None)

    def on_item_open__activate(self, widget):
        self.on_open__clicked(widget)

    def on_item_save_as__activate(self, widget):
        self.on_save__clicked(widget)

    def on_item_save__activate(self, widget):
        if self.last_filename_assigned:
            self.save_to(self.last_filename_assigned)
        else:
            self.on_save__clicked(widget)


    def show_confirm_dialog(self):
        leave = self.view.leave
        response = leave.run()
        leave.hide()
        return response


def main():
    app = Application()
    app.view.window.show()
    gtk.main()


if __name__ == '__main__':
    main()
