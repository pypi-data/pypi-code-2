# -*- coding: utf-8 -*-
import pygraphviz as pgv
import parser
import pac_parser

class Diagram:
    """Representa un diagrama completo."""

    def __init__(self, disable_visible_warnings=False):
        self.content = []
        self.digraph = pgv.AGraph(strict=False, directed=True, rankdir="BT", nodesep="0.75")
        self.nodes = {}
        self.disable_visible_warnings = disable_visible_warnings
        self.error_messages = []

    def add_warning_message(self, message):
        "Mustra un mensaje de advertencia en el diagrama."

        self.error_messages.append("Cuidado: " + message)

        if not self.disable_visible_warnings:
            self.digraph.add_node(message, shape='record', color='red3',
                    fontcolor='red3', fontsize='10', fontname='verdana')
            #, shape='record', fontsize='10',
            #    fontname="Verdana", color="red3",
            #    fontcolor="red3", label="cuidado: \n" + message)

    def read(self, input_file_name):
        "Lee un modelo de clases desde un archivo de texto."

        if self._is_pac_filename(input_file_name):
            file_handler = pac_parser.get_fakefile(input_file_name)
        else:
            file_handler = open(input_file_name, 'rt')

        self.read_from_file_handler(file_handler)

    def read_from_file_handler(self, file_handler):
        filecontent = file_handler.readlines()
        self.read_from_string(filecontent)
        file_handler.close()

    def _is_pac_filename(self, input_file_name):
        "Informa si un nombre de archivo parece un archivo .pac"
        return input_file_name.lower().endswith(".pac")

    def read_from_string(self, filecontent):
        "Lee un modelo de clases desde una lista de cadenas."

        models, relationships, errors = \
            parser.create_models_and_relationships_from_list(filecontent)

        # TODO: que la funcion reporte solamente la lista vacia en lugar de
        #       un solo valor como None.
        if models == [None]:
            self.add_empty_node()
        else:
            for model in models:
                self.add_model(model)

        self.create_hierarchy_relationships()
        self.create_explicit_relationships(relationships)

        for x in errors:
            self.error_messages.append(x)

    def add_model(self, model):
        "Genera un nodo de clase para el modelo indicado."

        model_content = model.get_content_as_string()
        node = self.digraph.add_node(str(model.name), shape='record', fontsize='10',
                                     fontname='Verdana', 
                                     label=model_content)
        if model.name:
            name = model.name
        else:
            name = "??"

        self.nodes[name] = (model.superclass, name)

    def add_empty_node(self):
        "Genera un nodo indicando que el modelo está vacío."

        node = self.digraph.add_node("Empty model", shape='none',
                                     fontsize='10', fontname="Verdana")

    def get_node_from_name(self, name):
        """Obtiene un nodo asociado a un determinado nombre de clase.

        Este método intenta reconocer clases por su nombre incluso si
        difieren en cantidad (ej. Auto ~= autos)."""

        # TODO: delegar en otro método e incluir casos como Pez ~= peces.
        # ver diveintopython
        name = name.lower()
        all_names = {}

        for x in self.nodes.keys():
            all_names[x.lower()] = self.nodes[x][1]

        if not all_names.has_key(name):
            name_without_last_word = name[:-1]

            if all_names.has_key(name_without_last_word):
                return all_names[name_without_last_word]
        
        return all_names[name]

    def create_hierarchy_relationships(self):
        for key, value in self.nodes.items():
            superclass, node = value


            if superclass:
                #superclass_node = self.get_node_from_name(superclass)
                edge = self.digraph.add_edge(node, superclass, 
                        arrowhead='onormal',
                        arrowtai='none')

    def create_explicit_relationships(self, relationships):
        """Genera las relaciones que el usuario indica manualmente.

        Estas relaciones se definen en el modelo de datos
        utilizando una sintaxis como::
        
            1 Vehiculo tiene * Pasajeros
        """

        for rel in relationships:
            try:
                from_node = self.get_node_from_name(rel.from_name)
                to_node = self.get_node_from_name(rel.to_name)
            except KeyError, msg:
                msg_error = u"No se encuentra la clase %s para dibujar la relación."
                self.add_warning_message(msg_error %(msg))
                return

            self.create_relation(from_node, to_node, rel)

    def create_relation(self, from_node, to_node, rel):

        edge = self.digraph.add_edge(from_node, to_node, 
                arrowhead=rel.arrowtail,
                arrowtail=rel.arrowhead,
                dir='both',
                label=rel.description,
                fontsize='10', 
                fontname='Verdana',
                taillabel=rel.from_counter, 
                headlabel=rel.to_counter)

    def save(self, filename, format, disable_output=False):
        self.digraph.layout(prog='dot')
        self.digraph.draw(filename, format)

        if not disable_output:
            print "Creating file: %s" %(filename)

            for message in self.error_messages:
                print  message

        return self.error_messages



        

if __name__ == '__main__':
    diagram = Diagram()
    code = """
A
    bb

    SubA
        a

B
    no


A -> B
"""

    diagram.read_from_string(code.split('\n'))
    diagram.save('test.png', 'png')
