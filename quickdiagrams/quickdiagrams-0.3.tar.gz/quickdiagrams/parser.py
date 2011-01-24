# -*- coding: utf-8 -*-
import re

ARROWS = ["->", "<-", "<>->", "<-<>", "<>-", "<\*>-", "-<>", "-<\*>"]

class RelationFactory:
    
    def __init__(self):
        self.patterns = self._create_relation_patterns()

    def is_relation(self, string):
        "Informa si una determinada cadena parece una relación."


        for pattern, describe in self.patterns:
            if pattern.match(string):
                return True

    def create_relation(self, string):
        "Genera un modelo de la relación."

        for pattern, describe in self.patterns:
            if pattern.match(string):
                return Relation(string, describe)

    def _create_relation_patterns(self):
        "Genera todas los patrones de relaciones reconocibles."

        pattern_strings = [
            "from_counter from_name description to_counter to_name",
            "from_counter from_name to_counter to_name",
            "from_name to_name",
            "from_name description to_name",
        ]

        re_patters = [(re.sub('\w+', '\S+', line), line) for line in pattern_strings]
        patterns = [(re.compile("^" + pattern + "$", re.IGNORECASE), line) 
                    for (pattern, line) in re_patters]
        

        rels = "|".join(ARROWS)
        line = u"\w+ (%s) \w+" %(rels)

        patterns.append((re.compile(line), "from_name arrow_description to_name"))

        return patterns


class Relation:

    def __init__(self, line, describe):
        line = line.strip()
        self.init()
        self._set_relation_values(line, describe)

    def init(self):
        self.from_counter = ''
        self.from_name = ''
        self.description = ''
        self.to_counter = ''
        self.to_name = ''
        self.arrowhead = 'none'
        self.arrowtail = 'none'

    def _set_relation_values(self, line, describe):
        "Define el valor de los atributos que cita la relación."

        for name, value in zip(describe.split(), line.split()):
            if name == "description":
                self._set_arrow_type(value)
            else:
                self.arrowtail = "normal"
                setattr(self, name, value)

    def _set_arrow_type(self, value):
        if value == "->":
            print "Linea normal"
            self.arrowtail = "normal"
        elif value == "<-":
            self.arrowhead = "normal"
        elif value == "<>->":
            self.arrowhead = "odiamond"
            self.arrowtail = "normal"
        elif value == "<-<>":
            self.arrowhead = "normal"
            self.arrowtail = "odiamond"
        elif value == "<>-":
            self.arrowhead = "odiamond"
        elif value == "<*>-":
            self.arrowhead = "diamond"
        elif value == "-<>":
            self.arrowtail = "odiamond"
        elif value == "-<*>":
            self.arrowtail = "diamond"
        elif value == "-":
            self.arrowhead = "normal"
        else:
            self.description = value
            self.arrowtail = "normal"


class Model:
    """Representa un modelo de objeto en el diagrama."""

    def __init__(self, name, superclass):
        self.name = name
        self.superclass = superclass
        self.attributes = []
        self.methods = []
        self.are_in_method_area = False

    def add(self, value):
        """Agrega un elemento que puede ser atributo o metodo."""
        
        if self._it_seems_like_a_method(value):
            self.methods.append(value)
        elif self._is_invisible(value):
            self.attributes.append("")
        elif self._is_contour(value):
            self.are_in_method_area = True
        else:
            if not self.are_in_method_area:
                self.attributes.append(value)
            else:
                self.methods.append(value)


    def _it_seems_like_a_method(self, word):
        """Indica si la palabra representa un nombre de metodo."""
        if ':' in word or '(' in word:
            return True

    def _is_invisible(self, line):
        return re.search("^\s*_$", line)

    def _is_contour(self, line):
        return re.search("^\s*--+$", line)

    def get_content_as_string(self):
        "Obtiene una representación estilo graphviz para dibujar."
        attributes = "\\n".join(self.attributes)
        methods = "\\n".join(self.methods)
        return "{%s|%s|%s}" %(self.name, attributes, methods)


def get_identation_width(line):
    "Reporta la longitud de una identacion."
    i = 0
    line = line.replace("\t", " " * 4)  # asume tabulacion de 4 espacios

    for c in line:
        if c == ' ':
            i += 1
        else:
            break

    return i

def is_empty(line):
    "Informa si la linea no tiene caracteres."
    return bool(line.strip())

def is_comment(line):
    return line.startswith('#') or line.startswith('//')

def is_invalid_syntax(line):
    return re.search(r"^\s*(\w|:|\(|\)|,|\.|\ |ñ|\+|-|#|Ñ|á|é|í|ó|ú|Á|É|Í|Ó)*$", line) or re.search("^\s*--+$", line)


# Enumeraciones
STATE_STARTING, STATE_POPULATING = range(2)

def create_models_and_relationships_from_list(list):
    identation_column = 0
    previous_identation_column = 0
    relation_factory = RelationFactory()
    relationships = []
    errors = []

    previous_line = None
    state = STATE_STARTING
    models = []
    model = None
    actual_father = []
    minimum_width = 4

    for number_line, line in enumerate(list):
        if not is_empty(line) or is_comment(line):
            continue

        if relation_factory.is_relation(line):
            relationships.append(relation_factory.create_relation(line))
            continue

        if not is_invalid_syntax(line):
            errors.append("Error de sintaxis, linea %d: '%s'" %(number_line + 1, line.rstrip()))
            continue

        identation_column = get_identation_width(line)

        # Intenta determinar el tamano de tabulacion que usa el usuario.
        if identation_column > 0:
            minimum_width = min(identation_column, minimum_width)

        if identation_column > previous_identation_column:
            previous_identation_column = previous_identation_column

            # Encuentra una subclase mientras carga el modelo.
            if state == STATE_POPULATING:
                if model:
                    models.append(model)
                    state = STATE_STARTING

            # Comienza a definir los atributos de la clase.
            if state == STATE_STARTING:
                state = STATE_POPULATING

                # Determina la superclase del modelo actual.
                if model:
                    if actual_father:
                        superclass = actual_father[-1]
                    else:
                        superclass = None
                else:
                    superclass = None

                model = Model(previous_line, superclass)

            actual_father.append(previous_line)

        elif identation_column < previous_identation_column:

            if state == STATE_POPULATING:
                model.add(previous_line)

            # determina la cantidad de identacion que ha eliminado
            i = (previous_identation_column - identation_column) / minimum_width


            for n in range(i):
                try:
                    a = actual_father.pop()
                except IndexError:
                    pass
        else:

            if state == STATE_POPULATING:
                model.add(previous_line)

        previous_identation_column = identation_column
        previous_line = line.strip()

    if state == STATE_POPULATING:
        model.add(previous_line)
    elif state == STATE_STARTING:
        # El modelo solo tiene una clase
        if previous_line:
            model = Model(previous_line, None)

    models.append(model)
    return models, relationships, errors
