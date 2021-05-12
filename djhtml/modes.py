import re


class Mode:
    """
    Base class for different modes.

    """

    def __init__(self, line):
        self.line = line

    def get_line(self, level):
        if self.line:
            return self.format_line(level + self.thislevel)
        return ""

    def format_line(self, level):
        return "    " * level + self.line.lstrip()

    @property
    def thislevel(self):
        return 0

    @property
    def nextlevel(self):
        return 0

    @property
    def nextmode(self):
        raise NotImplementedError()


class Django(Mode):
    """
    Mode to parse Django template tags. Used by all other modes
    (except comments).

    """

    TAG = re.compile(r"\{% +([a-z]+)")
    OPENING_TAGS = [
        "if",
        "ifchanged",
        "for",
        "block",
        "with",
        "filter",
        "verbatim",
        "spaceless",
        "autoescape",
        "blocktrans",
        "blocktranslate",
    ]
    OPENING_AND_CLOSING_TAGS = [
        "elif",
        "else",
        "empty",
    ]
    CLOSING_TAGS = [
        "endif",
        "endifchanged",
        "endfor",
        "endblock",
        "endwith",
        "endfilter",
        "endverbatim",
        "endspaceless",
        "endautoescape",
        "endblocktrans",
        "endblocktranslate",
    ]

    def __init__(self, line):
        self.line = line
        self.parse_line()

    def parse_line(self):
        self.tags = []
        for tag in self.TAG.finditer(self.line):
            if tag.group(1) in self.OPENING_TAGS:
                self.tags.append(1)
            elif tag.group(1) in self.CLOSING_TAGS:
                self.tags.append(-1)

    @property
    def thislevel(self):
        level = 0
        if tag := self.TAG.match(self.line.lstrip()):
            if tag.group(1) in self.OPENING_AND_CLOSING_TAGS:
                level = -1
            for tag in self.tags:
                if tag < 0:
                    level += tag
                else:
                    break
        return level

    @property
    def nextlevel(self):
        return sum(self.tags)


class HTML(Mode):
    """
    Mode to indent HTML tags. Makes no attempt at tree-building, just
    indents whenever there are more opening than closing tags on a
    line.

    """

    TAG = re.compile(r"</?([a-z]+) ?[^>]*>?")
    IGNORE_TAGS = [
        "br",
        "hr",
        "img",
        "link",
        "meta",
    ]

    def __init__(self, line):
        self.line = line
        self.django = Django(line)
        self.parse_line()

    def parse_line(self):
        self.tags = []
        for tag in self.TAG.finditer(self.line):
            if tag.group(1) in self.IGNORE_TAGS or tag.group(0)[-2] == "/":
                continue
            elif tag.group(0)[1] == "/":
                self.tags.append(-1)
            else:
                self.tags.append(1)

    @property
    def thislevel(self):
        level = 0
        if self.TAG.match(self.line.lstrip()):
            for tag in self.tags:
                if tag < 0:
                    level += tag
                else:
                    break
        return level + self.django.thislevel

    @property
    def nextlevel(self):
        return sum(self.tags) + self.django.nextlevel

    @property
    def nextmode(self):
        if "{% comment %}" in self.line and "{% endcomment %" not in self.line:
            return Comment
        if "<style" in self.line and "</style" not in self.line:
            return CSS
        if "<script" in self.line and "</script" not in self.line:
            return JS
        return self.__class__


class CSS(Mode):
    """
    Indent CSS rules by counting braces.

    """

    def __init__(self, line):
        self.line = line
        self.django = Django(line)
        self.parse_line()

    def parse_line(self):
        self.braces = []
        for char in self.line:
            if char == "{":
                self.braces.append(1)
            elif char == "}":
                self.braces.append(-1)

    @property
    def thislevel(self):
        level = 0
        if self.line.lstrip().startswith("}"):
            for brace in self.braces:
                if brace < 0:
                    level += brace
                else:
                    break
        if self.nextmode is not self.__class__:
            level -= 1
        return level + self.django.thislevel

    @property
    def nextlevel(self):
        level = sum(self.braces)
        if self.nextmode is not self.__class__:
            level -= 1
        return level + self.django.nextlevel

    @property
    def nextmode(self):
        if "</style>" in self.line:
            return HTML
        return self.__class__


class JS(CSS):
    """
    Same as CSS mode.

    """

    @property
    def nextmode(self):
        if "</script>" in self.line:
            return HTML
        return self.__class__


class Comment(Mode):
    """
    Mode for Django comments. Preserves all whitespace within them.

    """

    def get_line(self, level):
        return self.line

    @property
    def nextmode(self):
        if "{% endcomment %}" in self.line:
            return HTML
        return self.__class__
