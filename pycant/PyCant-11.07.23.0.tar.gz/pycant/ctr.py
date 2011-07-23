"""Reader and writer of Cantata++ test results.

Currently, this package is mainly oriented towards structural coverage
results.
"""

import math
import re



class SummableObject(object):
    """Abstracted object which instances can be cumulated, provided that they
    are compatible.
    """

    def is_summable(self, other):
        """SO.is_summable() -> boolean

        True iff both instances are compatible with each other for
        accumulation.
        """
        raise NotImplementedError


    def sum(self, other):
        """SO.sum() -> None

        Acumulate in-place both instances without verifying their
        compatibility.
        """
        raise NotImplementedError



class AccessCounter(SummableObject):
    """Access counter. Can integrate a notion of saturation.

    If limit is negative, which is the default behaviour, the access
    counter does not saturate. Otherwise, it cannot go further than the
    limit value.

    Summing AccessCounter may lower the saturation limit, never raise it.
    This way, AccessCounter can never go insaturated after being saturated.
    """

    __slots__ = [
        'count',
        'limit',
        ]


    def __init__(self, limit = -1):
        super(AccessCounter, self).__init__()

        self.count = 0
        self.limit = limit


    def __str__(self):
        if self.count == 0:
            return ">> NOT EXECUTED "
        elif self.limit < 0 \
                or self.count < self.limit:
            return "%16s" % self.count
        else:
            return ">=%s" % self.count


    def is_summable(self, other):
        return True


    def sum(self, other):
        # Restrict the upper limit if necessary
        if other.limit >= 0:
            if self.limit < 0:
                self.limit = other.limit
            else:
                self.limit = min(self.limit, other.limit)

        # Determine what the count should be with the new upper limit
        cumulated_count = self.count + other.count
        if self.limit < 0:
            self.count = cumulated_count
        else:
            self.count = min(cumulated_count, self.limit)



class Instruction(SummableObject):
    """Executable code instruction.
    """

    __slots__ = [
        'access',
        'index',
        'kind',
        ]


    def __init__(self):
        super(Instruction, self).__init__()

        # Distance to the start of the Function (in line of code)
        self.index = None
        # Kind, as determined by Cantata++: cond, other, return, etc.
        self.kind = None
        # Execution counter
        self.access = None


    def is_summable(self, other):
        return self.index == other.index \
            and self.kind == other.kind


    def sum(self, other):
        self.access += other.access



class Function(SummableObject):
    """C-language function representation.
    """

    __slots__ = [
        'file',
        'function',
        'index',
        'instructions',
        'parameters',
        'parents',
        ]


    def __init__(self):
        super(Function, self).__init__()

        # Record of all .ctr files that have participated in current state
        self.parents = list()

        # Strings identifying the Function: source filename, function name
        # and parameters list
        self.file = None
        self.function = None
        self.parameters = None

        # Line index of the function in the source code, as defined by its
        # first parent.
        self.index = None

        # Ordered set of Instructions
        self.instructions = list()


    def __str__(self):
        result = ""
        nb_executed = 0
        nb_total = 0

        # Header
        j = self.parameters.find(" ")
        header1 = "%s(%d):%s(%s" % (self.file,
                                    self.index,
                                    self.function,
                                    self.parameters[:j])
        header2 = self.parameters[j:] + ")"

        i = 0
        while i + 79 <= len(header1):
            result += header1[i:i + 79] + "\n"
            i += 79
        result += header1[i:]
        length = 79 - (len(header1) - i)

        i = 0
        while i + length <= len(header2):
            j = header2.rfind(" ", i, i + length + 1)
            if j == -1:
                result += header2[i:i + length] + "\n"
                i += length
            else:
                result += header2[i:j] + "\n"
                if j < i + length:
                    i = j
                    while i < len(header2) and header2[i] == " ":
                        i += 1
                else:
                    i = j
            length = 79
        if i < len(header2):
            result += header2[i:] + "\n"

        result += "statement coverage details" \
            + " (with executed and un-executed cases)\n\n"

        # Instructions
        for index, instruction in enumerate(self.instructions):
            # Ending of the source filename, followed by the line number of the
            # instruction shall be 22 characters maximum
            file_line = "{}({}):".format(self.file,
                                         self.index + instruction.index)
            file_line = file_line[-22:]

            result += "{:22s}{:>11s}{:4d} ".format(file_line,
                                                   "stmnt",
                                                   index + 1)
            if instruction.kind is None:
                result += " " * 13
            else:
                result += "{:13s}".format("(" + instruction.kind + ")")

            result += "{:>26s}\n".format(str(instruction.access))

            # Gathering some information for the global status
            nb_total += 1
            if instruction.access.count > 0:
                nb_executed += 1

        # Global status
        result += "\n"
        suffix = '"' + self.function[-30:] + '"'
        result += "{:32s}{:>33s}{:12d}\n".format(suffix,
                                                 "executed",
                                                 nb_executed)
        result += "{:32s}{:>33s}{:12d}\n".format(suffix,
                                                 "un-executed",
                                                 nb_total - nb_executed)

        if nb_executed < nb_total:
            rate = (1000 * nb_executed / nb_total) / 10.0
        else:
            rate = 100.0

        result += "{:32s}{:>33s}{:11.1f}%\n".format(suffix,
                                                    "statement coverage",
                                                    rate)

        return result


    def is_summable(self, other):
        if self.file != other.file \
                or self.function != other.function \
                or self.parameters != other.parameters:
            return False

        if len(self.instructions) != len(other.instructions):
            return False

        for i in range(len(self.instructions)):
            if not self.instructions[i].is_summable(other.instructions[i]):
                return False

        return True


    def sum(self, other):
        self.parents.extend(other.parents)
        for i in range(len(self.instructions)):
            self.instructions[i].sum(other.instructions[i])


    def coverage(self):
        """Executed Instructions ratio
        """
        result = 1.0

        nb_total = len(self.instructions)
        nb_executed = 0
        for instruction in self.instructions:
            if instruction.access.count > 0:
                nb_executed += 1

        if nb_executed < nb_total:
            result = float(nb_executed) / nb_total

        return result


    def nb_ok(self):
        """Count of executed Instructions (at least one access)
        """
        return len([i for i in self.instructions if i.access.count > 0])


    def nb_instructions(self):
        """Total number of Instructions
        """
        return len(self.instructions)



class TestResult(object):
    """Retained content of a Cantata++ test result file - '.ctr' suffix.

    Currently it is limited to test cases'names and functions structural
    coverage results.
    """

    __slots__ = [
        'filename',
        'functions',
        'test_cases',
        ]


    def __init__(self):
        self.filename = None
        self.test_cases = set()
        self.functions = set()



class Import(object):
    """Reads a '.ctr' file and convert it to a TestResult.
    """

    def __init__(self):
        self._load_result = None

        self._lines = list()
        self._contexts = list()

        self._lineset_cache = None
        self._lineset_start = 0
        self._lineset_last = 0


    def load(self, filename):
        """I.load(...) -> TestResult

        Analyses '.ctr' file to build up a TestResult instance.
        If file access is difficult, IOError may be raised.
        """
        self._load_result = TestResult()
        self._load_result.filename = filename

        # Complete load of the text file before further analysis
        stream = open(filename, "r")
        for line in stream:
            self._lines.append(line.rstrip())
        self._push_context(0, len(self._lines) - 1)

        # Textual analysis
        state = 0
        for index, line in enumerate(self._lines):
            if state == 0:
                # Test cases'names are collected
                if line.find("Start Test:") != -1 \
                        and line.find("Coverage Analysis") == -1:
                    test_case = line.split()[3]
                    self._load_result.test_cases.add(test_case)

                # Identifying structural coverage results is much more
                # complicated, and requires a finite state automaton
                if re.search("\(\d+\):", self._lineset(index)):
                    state = 1
                    i_0 = index
            elif state == 1:
                if line.startswith("entry point coverage "):
                    state = 2
                elif re.search(": statement coverage", line):
                    state = 3
                elif re.search(" statement coverage", line):
                    self._push_context(i_0, index)
                    function = self._load_function()
                    function.parents.append(filename)
                    self._load_result.functions.add(function)
                    self._pop_context()
                    state = 0
            elif state == 2:
                if re.search(" entry point coverage", line):
                    state = 0
            elif state == 3:
                if line.startswith("-----"):
                    state = 0

        return self._load_result


    def _load_function(self):
        """Current context text is analysed to produce a Function.
        """
        result = Function()

        #######
        # HEADER
        #######

        # Isolation
        header = ""
        i = self._line_min()
        while self._lines[i + 1] != "":
            header += self._lines[i]
            if len(self._lines[i]) < 79:
                header += " "
            i += 1

        # Analysis
        match = re.match("(\w+\.\w+)\((\d+)\):(\w+)\(([^)]*)\)", header)
        result.file = match.group(1)
        result.index = int(match.group(2))
        result.function = match.group(3)
        result.parameters = match.group(4)

        #########
        # MEASURES
        #########

        # Structural coverage result
        i += 2
        while self._lines[i] != "":
            self._push_context(i, i)
            instruction = self._load_instruction()
            instruction.index -= result.index
            result.instructions.append(instruction)
            self._pop_context()
            i += 1

        return result


    def _load_instruction(self):
        """Current context text is analysed to produce an Instruction
        """
        result = Instruction()

        line = self._lines[self._line_min()]
        match = re.search("\((\d+)\).*(\(([a-z-]+)\))", line)
        if match:
            result.index = int(match.group(1))
            result.kind = match.group(3)
        else:
            match = re.search("\((\d+)\)", line)
            result.index = int(match.group(1))

        result.access = AccessCounter()
        if not line.endswith(">> NOT EXECUTED"):
            match = re.search("(>=)?(\d+)\Z", line)
            if match.group(1) is not None:
                result.access.limit = int(match.group(2))
            result.access.count = int(match.group(2))

        return result


    def _push_context(self, line_min, line_max):
        """Reduce text analysis scope to the proposed interval.
        """
        self._contexts.append((line_min, line_max))


    def _pop_context(self):
        """Go back to the previous text analysis scope.
        """
        self._contexts[:] = self._contexts[:-1]


    def _line_min(self):
        """First line index of the current analysis context
        """
        return self._contexts[-1][0]


    def _line_max(self):
        """Last line index of the current analysis context
        """
        return self._contexts[-1][1]


    def _lineset(self, index):
        """A lineset is the maximal set of adjacent lines that contains the one
        at the corresponding index, without including any so-called "separator
        line"

        If index designates a separator line, results is empty.
        """
        if index < self._lineset_start \
                or index >= self._lineset_last:
            self._lineset_cache = ""
            if not self._is_separator(index):
                self._lineset_start = index
                while self._lineset_start > self._line_min() \
                        and not self._is_separator(self._lineset_start - 1):
                    self._lineset_start -= 1
                self._lineset_last = index
                while self._lineset_last <= self._line_max() \
                        and not self._is_separator(self._lineset_last):
                    self._lineset_last += 1

                for i in range(self._lineset_start, self._lineset_last):
                    self._lineset_cache += self._lines[i]

        return self._lineset_cache


    def _is_separator(self, index):
        """True iff line at proposed index is a "separator line".
        Separator line can either be a blank line or a line that contains
        only hyphens.
        """
        return not re.match("[^-]", self._lines[index])



class Export(object):
    """Writes a set of Functions in a file according to the '.ctr' file format.
    """

    def dump(self, stream, *functions):
        """Write in the stream the structural coverage results of the functions
        and complete it with the global status of the set.
        """
        stats = list()

        for function in functions:
            stream.write(str(function))
            stream.write("\n")

            stats.append((function.coverage(), len(function.instructions)))

        # Global status of the whole set of functions
        status = \
            """Summary by     EXECUTED     Overall                Statistics
Coverage type  INFEASIBLES  (wavg)     avg /    min /    max /    dev /   num
-----------------------------------------------------------------------------
statement              0   %5.1f%%   %5.1f%% / %5.1f%% / %5.1f%% / %5.1f%% / %5d
-----------------------------------------------------------------------------
"""
        minimum = 1.0
        maximum = 0.0
        mean = 0.0
        weighted_mean = 0.0
        nb_instruction = 0
        for ratio, length in stats:
            mean += ratio
            weighted_mean += ratio * length
            nb_instruction += length
            if ratio < minimum:
                minimum = ratio
            if ratio > maximum:
                maximum = ratio
        if nb_instruction > 0:
            weighted_mean /= nb_instruction

        deviation = 0.0
        nb_function = len(stats)
        if nb_function > 1:
            mean /= nb_function
            for ratio, length in stats:
                deviation += (ratio - mean)**2
            deviation = math.sqrt(deviation / float(nb_function - 1))

        stream.write(status % (int(1000.0 * weighted_mean) / 10.0,
                            int(1000.0 * mean) / 10.0,
                            int(1000.0 * minimum) / 10.0,
                            int(1000.0 * maximum) / 10.0,
                            int(1000.0 * deviation) / 10.0,
                            nb_function))
