class Line:
    """
    A single output line including the final newline.

    """

    def __init__(self, tabwidth, initial_level):
        self.tabwidth = tabwidth
        self.initial_level = initial_level
        self.tokens = []
        self.offset = 0

    def append(self, token):
        self.tokens.append(token)

    @property
    def text(self):
        """
        The raw, unindented text of this line.

        """
        return "".join([str(token) for token in self.tokens]).strip()

    @property
    def dedent(self):
        """
        Whether this line should be dedented compared to the previous line.

        """
        for token in self.tokens:
            if token.dedent:
                return True
            if token.indent:
                return False
        return False

    @property
    def indent(self):
        """
        Whether the next line should be indented compared to this line.

        """
        for token in reversed(self.tokens):
            if token.indent:
                return True
            if token.dedent:
                return False
        return False

    @property
    def level(self):
        """
        This line's indentation level.

        """
        return self.initial_level - 1 if self.dedent else self.initial_level

    def __str__(self):
        if self.text:
            space = " " * self.tabwidth * self.level + " " * self.offset
            return space + self.text + "\n"
        return "\n"

    def __repr__(self):
        return repr(self.tokens)

    def __bool__(self):
        return bool(self.text)

    def __next__(self):
        level = self.level + 1 if self.indent else self.level
        return Line(self.tabwidth, level)
