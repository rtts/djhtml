class Line:
    """
    A single output line not including the final newline.

    The behavior regarding final newlines has changed between DjHTML
    v1.4.14 and v1.5.0. It used to always append the final newline,
    but now this will only happen when the source file already
    contains a final newline.

    See https://github.com/rtts/djhtml/issues/56 for the discussion
    that led to this change.

    """

    def __init__(self, nr=1):
        self.nr = nr
        self.tokens = []
        self.level = 0

    def append(self, token):
        """
        Append tokens to the line.

        """
        token.line_nr = self.nr
        self.tokens.append(token)

    @property
    def text(self):
        """
        The unindented text of this line without leading/trailing spaces.

        """
        return "".join([str(token) for token in self.tokens]).strip()

    def indent(self, tabwidth):
        """
        The final, indented text of this line. Make sure to set the level
        and optionally offset before calling this method.

        """
        if self.tokens:
            if self.tokens[0].ignore:
                return "".join([str(token) for token in self.tokens])
            elif self.text:
                offset = self.tokens[0].offset * tabwidth
                spaces = tabwidth * self.level + offset
                return " " * spaces + self.text
        return ""

    def __repr__(self):
        return repr(self.tokens)

    def __bool__(self):
        return bool(self.tokens and self.text)

    def __next__(self):
        return Line(nr=self.nr + 1)
